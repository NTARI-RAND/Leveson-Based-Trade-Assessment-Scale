"""Role-scoped history pages and complete accountability from one SQLite snapshot.

Licensed under GNU Affero General Public License v3.0.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass

from . import event_store


@dataclass(frozen=True)
class HistoryQuery:
    """Validated HTTP scope and independent collection continuations."""

    party: str
    role: str
    limit: int | None
    active_cursor: str | None = None
    dismissed_cursor: str | None = None


class InvalidCursorError(ValueError):
    """A continuation is malformed or belongs to a different history."""


def active_event(row: sqlite3.Row) -> dict:
    """Retain the existing active-event representation and accountability fields."""
    event = _event_fields(row)
    event.update(defaulted=row["rater_role"] == "system", **_contest_fields(row))
    return event


def _contest_fields(row: sqlite3.Row) -> dict:
    """Keep the complete contest trail when a rating is later dismissed."""
    fields = {"contested": row["contested_by"] is not None}
    if fields["contested"]:
        fields.update(
            contested_by=row["contested_by"],
            contest_reason=row["contest_reason"],
            contested_at=row["contested_at"],
            upheld=row["upheld_by"] is not None,
        )
        if fields["upheld"]:
            fields.update(
                upheld_by=row["upheld_by"],
                uphold_reason=row["uphold_reason"],
                upheld_at=row["upheld_at"],
            )
    return fields


def dismissed_event(row: sqlite3.Row) -> dict:
    """A dismissal forgives but never hides the original event or its reason."""
    event = _event_fields(row)
    if row["contested_by"] is not None:
        event.update(_contest_fields(row))
    event.update(
        dismissed_by=row["dismissed_by"],
        reason=row["dismissal_reason"],
        dismissed_at=row["dismissed_at"],
    )
    return event


def _event_fields(row: sqlite3.Row) -> dict:
    """Fields shared by legacy and paged event representations."""
    return {
        "event_id": row["id"],
        "value": row["value"],
        "category": row["category"],
        "comment": row["comment"],
        "exchange_id": row["exchange_id"],
        "rater": row["rater"],
        "rated_at": row["timestamp"],
    }


def _summary(conn: sqlite3.Connection, party: str, role: str) -> dict:
    """Aggregate the entire active history in SQL, not from the current page."""
    parameters = (party, role)
    active = """FROM rating_events re LEFT JOIN dismissals d ON d.event_id = re.id
                WHERE re.rated_party = ? AND re.role = ? AND d.event_id IS NULL"""
    distribution = {str(level): 0 for level in range(-1, 5)}
    for row in conn.execute(
        "SELECT re.value, COUNT(*) AS n " + active + " GROUP BY re.value", parameters
    ):
        distribution[str(row["value"])] = row["n"]
    row = conn.execute(
        """SELECT COUNT(*) AS total, COUNT(DISTINCT re.exchange_id) AS transaction_count,
                  MIN(re.timestamp) AS first_rated_at, MAX(re.timestamp) AS last_rated_at,
                  COALESCE(SUM(re.rater_role = 'system'), 0) AS defaulted_count """
        + active,
        parameters,
    ).fetchone()
    dismissed_distribution = {str(level): 0 for level in range(-1, 5)}
    for dismissed_row in conn.execute(
        """SELECT re.value, COUNT(*) AS n FROM rating_events re
           JOIN dismissals d ON d.event_id = re.id
           WHERE re.rated_party = ? AND re.role = ? GROUP BY re.value""",
        parameters,
    ):
        dismissed_distribution[str(dismissed_row["value"])] = dismissed_row["n"]
    return {
        "distribution": distribution,
        **dict(row),
        "dismissed_count": sum(dismissed_distribution.values()),
        "dismissed_distribution": dismissed_distribution,
        "harm_index": _harm_index(conn, party, role),
    }


def _harm_index(conn: sqlite3.Connection, party: str, role: str) -> list[dict]:
    """Every -1 or dismissal once, newest rating first; never page away harm."""
    rows = conn.execute(
        """SELECT re.id AS event_id, re.exchange_id, re.timestamp AS rated_at,
                  re.value, d.event_id AS dismissal_id, d.dismissed_by,
                  d.reason, d.timestamp AS dismissed_at, c.contested_by, u.upheld_by
           FROM rating_events re
           LEFT JOIN dismissals d ON d.event_id = re.id
           LEFT JOIN contests c ON c.event_id = re.id
           LEFT JOIN upholds u ON u.event_id = re.id
           WHERE re.rated_party = ? AND re.role = ?
             AND (re.value = -1 OR d.event_id IS NOT NULL)
           ORDER BY re.timestamp DESC, re.id DESC""",
        (party, role),
    )
    result = []
    for row in rows:
        dismissed = row["dismissal_id"] is not None
        item = {
            key: row[key] for key in ("event_id", "exchange_id", "rated_at", "value")
        }
        item.update(
            state="dismissed" if dismissed else "active",
            contested=row["contested_by"] is not None,
            upheld=row["upheld_by"] is not None,
        )
        if dismissed:
            item.update(
                {key: row[key] for key in ("dismissed_by", "reason", "dismissed_at")}
            )
        result.append(item)
    return result


def _anchor(
    conn: sqlite3.Connection, party: str, role: str, cursor: str | None, kind: str
) -> tuple[str, int] | None:
    """Resolve immutable ordering fields; a later dismissal cannot invalidate an anchor."""
    if cursor is None:
        return None
    if not re.fullmatch(kind + r":[1-9][0-9]{0,18}", cursor):
        raise InvalidCursorError("Invalid history cursor")
    event_id = int(cursor[2:])
    if event_id > 9223372036854775807:
        raise InvalidCursorError("Invalid history cursor")
    row = conn.execute(
        "SELECT timestamp, id FROM rating_events WHERE id = ? AND rated_party = ? AND role = ?",
        (event_id, party, role),
    ).fetchone()
    if row is None:
        raise InvalidCursorError("Cursor does not belong to this history")
    return tuple(row)


def _page(
    conn: sqlite3.Connection, query: HistoryQuery, cursor: str | None, kind: str
) -> tuple[list[dict], str | None]:
    """Read at most limit+1 rows; timestamp ties advance by immutable event ID."""
    anchor = _anchor(conn, query.party, query.role, cursor, kind)
    timestamp, event_id = anchor or (None, None)
    select = """SELECT re.*, c.contested_by, c.reason AS contest_reason, c.timestamp AS contested_at,
                  u.upheld_by, u.reason AS uphold_reason, u.timestamp AS upheld_at,
                  d.dismissed_by, d.reason AS dismissal_reason, d.timestamp AS dismissed_at
           FROM rating_events re
           LEFT JOIN dismissals d ON d.event_id = re.id
           LEFT JOIN contests c ON c.event_id = re.id
           LEFT JOIN upholds u ON u.event_id = re.id
           WHERE re.rated_party = :party AND re.role = :role
             AND (d.event_id IS NULL) = :active"""
    # Separate the equal-timestamp range so SQLite can seek on both index keys,
    # including histories whose events all share one timestamp.
    sql = select
    if anchor:
        sql = (
            select
            + " AND re.timestamp = :timestamp AND re.id > :event_id"
            + " UNION ALL "
            + select
            + " AND re.timestamp > :timestamp"
        )
    rows = conn.execute(
        sql + " ORDER BY timestamp, id LIMIT :limit",
        {
            "party": query.party,
            "role": query.role,
            "active": kind == "a",
            "timestamp": timestamp,
            "event_id": event_id,
            "limit": query.limit + 1,
        },
    ).fetchall()
    continuation = (
        f"{kind}:{rows[query.limit - 1]['id']}" if len(rows) > query.limit else None
    )
    serialize = active_event if kind == "a" else dismissed_event
    return [serialize(row) for row in rows[: query.limit]], continuation


def read_history(conn: sqlite3.Connection, query: HistoryQuery) -> dict:
    """One request sees one snapshot, including annotations and full-history totals."""
    conn.execute("BEGIN")
    try:
        summary = _summary(conn, query.party, query.role)
        if query.limit is None:
            return {
                "rated_party": query.party,
                "role": query.role,
                **summary,
                "events": [
                    active_event(row)
                    for row in event_store.get_events_for_party_role(
                        conn, query.party, query.role
                    )
                ],
                "dismissed": [
                    dismissed_event(row)
                    for row in event_store.get_dismissed_events_for_party_role(
                        conn, query.party, query.role
                    )
                ],
            }
        events, next_active = _page(conn, query, query.active_cursor, "a")
        dismissed, next_dismissed = _page(conn, query, query.dismissed_cursor, "d")
        return {
            "rated_party": query.party,
            "role": query.role,
            **summary,
            "events": events,
            "dismissed": dismissed,
            "pagination": {
                "limit": query.limit,
                "next_active_cursor": next_active,
                "next_dismissed_cursor": next_dismissed,
            },
        }
    finally:
        conn.rollback()
