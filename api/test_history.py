"""HTTP history regressions against local SQLite. Run: python -m unittest api.test_history.

Licensed under GNU Affero General Public License v3.0.
"""

import os
import sqlite3
import tempfile
import tracemalloc
import unittest
from contextlib import closing
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import event_store
from api.main import app


class HistoryTests(unittest.TestCase):
    """Catch truncated summaries, missing accountability and unstable pagination."""

    def setUp(self) -> None:
        """Keep every request on an isolated local database."""
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = os.path.join(self.directory.name, "history.db")
        self.connect = event_store.get_connection
        for context in (
            patch.dict(os.environ, {"LBTAS_API_KEY": "history-test-key"}),
            patch.object(event_store, "get_connection", side_effect=self.connection),
        ):
            self.addCleanup(context.stop)
            context.start()
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.headers = {"X-API-Key": "history-test-key"}
        self.url = "/ratings/Bob/market_seller"
        self.seed_history()

    def seed_history(self) -> None:
        """Seed distinct levels, a shared exchange, annotations and isolated roles."""
        with closing(self.connection()) as conn, conn:
            rows = [
                (1, "shared", "a", "Bob", "market_seller", -1, "party"),
                (2, "shared", "b", "Bob", "market_seller", 0, "party"),
                (3, "third", "c", "Bob", "market_seller", 1, "party"),
                (4, "fourth", "system", "Bob", "market_seller", 2, "system"),
                (5, "fifth", "e", "Bob", "market_seller", 3, "party"),
                (6, "sixth", "f", "Bob", "market_seller", 4, "party"),
                (7, "seventh", "g", "Bob", "market_seller", 2, "party"),
                (8, "dismissed-one", "h", "Bob", "market_seller", -1, "party"),
                (9, "dismissed-two", "i", "Bob", "market_seller", -1, "party"),
                (10, "other-role", "j", "Bob", "market_buyer", -1, "party"),
                (11, "other-party", "k", "Carol", "market_seller", -1, "party"),
            ]
            conn.executemany(
                """INSERT INTO rating_events
                (id, exchange_id, rater, rated_party, role, value, rater_role, comment, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Local explanation', '2026-01-01T00:00:00+00:00')""",
                rows,
            )
            conn.execute(
                "UPDATE rating_events SET timestamp = '2026-01-03T00:00:00+00:00' WHERE id = 7"
            )
            conn.executemany(
                "INSERT INTO dismissals (event_id, dismissed_by, reason, timestamp) VALUES (?, 'operator', 'Bad faith', '2026-01-04')",
                [(8,), (9,)],
            )
            conn.execute(
                "INSERT INTO contests (event_id, contested_by, reason, timestamp) VALUES (5, 'Bob', 'Disputed', '2026-01-02')"
            )
            conn.execute(
                "INSERT INTO upholds (event_id, upheld_by, reason, timestamp) VALUES (5, 'operator', 'Evidence checked', '2026-01-03')"
            )

    def connection(self, *args, **kwargs) -> sqlite3.Connection:
        """Use a real independent connection for each request."""
        return self.connect(self.path, *args, **kwargs)

    def read(self, **params) -> dict:
        """Read through the mounted HTTP route, including query validation."""
        response = self.client.get(self.url, params=params, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        if "limit" in params:
            self.assertIn("pagination", response.json())
        return response.json()

    def test_page_keeps_full_history_summary(self) -> None:
        result = self.read(limit=2)
        self.assertEqual(len(result["events"]), 2)
        self.assertEqual(
            result["distribution"], {"-1": 1, "0": 1, "1": 1, "2": 2, "3": 1, "4": 1}
        )
        self.assertEqual(result["total"], 7)
        self.assertEqual(result["transaction_count"], 6)
        self.assertEqual(result["defaulted_count"], 1)
        self.assertEqual(result["dismissed_count"], 2)
        self.assertEqual(result["first_rated_at"], "2026-01-01T00:00:00+00:00")
        self.assertEqual(result["last_rated_at"], "2026-01-03T00:00:00+00:00")

    def test_equal_timestamp_pages_cover_each_active_event_once(self) -> None:
        result = self.read(limit=2)
        ids = [row["event_id"] for row in result["events"]]
        while result["pagination"]["next_active_cursor"] is not None:
            result = self.read(
                limit=2, active_cursor=result["pagination"]["next_active_cursor"]
            )
            ids.extend(row["event_id"] for row in result["events"])
        self.assertEqual(ids, [1, 2, 3, 4, 5, 6, 7])

    def test_every_dismissal_remains_navigable_with_its_annotation(self) -> None:
        first = self.read(limit=1)
        second = self.read(
            limit=1, dismissed_cursor=first["pagination"]["next_dismissed_cursor"]
        )
        self.assertEqual(
            [first["dismissed"][0]["event_id"], second["dismissed"][0]["event_id"]],
            [8, 9],
        )
        self.assertIsNone(second["pagination"]["next_dismissed_cursor"])
        for result in (first, second):
            row = result["dismissed"][0]
            self.assertEqual(row["dismissed_by"], "operator")
            self.assertEqual(row["reason"], "Bad faith")
            self.assertEqual(row["comment"], "Local explanation")
            self.assertEqual(result["dismissed_count"], 2)

    def test_page_preserves_timeout_and_contest_uphold_annotations(self) -> None:
        result = self.read(limit=7)
        self.assertTrue(result["events"][3]["defaulted"])
        upheld = result["events"][4]
        self.assertTrue(upheld["contested"])
        self.assertTrue(upheld["upheld"])
        self.assertEqual(upheld["contested_by"], "Bob")
        self.assertEqual(upheld["uphold_reason"], "Evidence checked")

    def test_dismissed_history_preserves_prior_contest_and_uphold(self):
        """A dismissal must not erase earlier adjudication in either read path."""
        with closing(self.connection()) as conn, conn:
            conn.execute(
                "INSERT INTO dismissals (event_id, dismissed_by, reason, timestamp) VALUES (5, 'operator', 'Forgiven', '2026-01-05')"
            )
        for params in ({}, {"limit": 100}):
            with self.subTest(params=params):
                row = next(
                    row
                    for row in self.read(**params)["dismissed"]
                    if row["event_id"] == 5
                )
                self.assertIn("contested", row)
                self.assertTrue(row["contested"])
                self.assertEqual(row["contested_by"], "Bob")
                self.assertEqual(row["contest_reason"], "Disputed")
                self.assertEqual(row["contested_at"], "2026-01-02")
                self.assertTrue(row["upheld"])
                self.assertEqual(row["upheld_by"], "operator")
                self.assertEqual(row["uphold_reason"], "Evidence checked")
                self.assertEqual(row["upheld_at"], "2026-01-03")
                self.assertEqual(row["reason"], "Forgiven")

    def test_pending_contest_remains_visible_without_uphold(self):
        """Dropping unresolved contest details must fail for both read modes."""
        with closing(self.connection()) as conn, conn:
            conn.execute("INSERT INTO contests (event_id, contested_by, reason, timestamp) VALUES (3, 'Bob', 'Pending review', '2026-01-02')")
        for params in ({}, {"limit": 7}):
            row = self.read(**params)["events"][2]
            self.assertEqual(row, {
                "event_id": 3, "value": 1, "category": None,
                "comment": "Local explanation", "exchange_id": "third",
                "rater": "c", "rated_at": "2026-01-01T00:00:00+00:00",
                "defaulted": False, "contested": True, "contested_by": "Bob",
                "contest_reason": "Pending review", "contested_at": "2026-01-02",
                "upheld": False,
            })

    def test_unpaged_response_retains_existing_contract(self) -> None:
        result = self.read()
        self.assertNotIn("pagination", result)
        self.assertEqual(
            [row["event_id"] for row in result["events"]], [1, 2, 3, 4, 5, 6, 7]
        )
        self.assertEqual([row["event_id"] for row in result["dismissed"]], [8, 9])
        self.assertEqual(result["total"], 7)

    def test_invalid_limits_and_cursors_fail_without_returning_history(self) -> None:
        """Distinguish HTTP query validation from invalid continuation semantics."""
        for params, status in (
            ({"limit": 0}, 422),
            ({"limit": 101}, 422),
            ({"limit": "bad"}, 422),
            ({"active_cursor": "a:1"}, 400),
            ({"limit": 1, "active_cursor": "bad"}, 400),
            ({"limit": 1, "active_cursor": "d:8"}, 400),
            ({"limit": 1, "active_cursor": "a:10"}, 400),
            ({"limit": 1, "dismissed_cursor": "d:11"}, 400),
            ({"limit": 1, "active_cursor": "a:9223372036854775808"}, 400),
            ({"limit": 1, "active_cursor": "a:" + "1" * 20}, 422),
        ):
            with self.subTest(params=params):
                response = self.client.get(self.url, params=params, headers=self.headers)
                self.assertEqual(response.status_code, status)
                self.assertNotIn("events", response.json())

    def test_paged_reads_keep_fail_closed_authorization(self) -> None:
        for headers in ({}, {"X-API-Key": "wrong"}):
            response = self.client.get(self.url, params={"limit": 1}, headers=headers)
            self.assertEqual(response.status_code, 401)
        with patch.dict(os.environ, {"LBTAS_API_KEY": ""}):
            response = self.client.get(
                self.url, params={"limit": 1}, headers=self.headers
            )
            self.assertEqual(response.status_code, 503)

    def test_empty_history_is_404_and_all_dismissed_history_is_visible(self):
        response = self.client.get(
            "/ratings/Nobody/market_seller", params={"limit": 1}, headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
        with closing(self.connection()) as conn, conn:
            conn.execute(
                "INSERT INTO dismissals (event_id, dismissed_by, reason, timestamp) VALUES (10, 'operator', 'Resolved', '2026-01-04')"
            )
        response = self.client.get(
            "/ratings/Bob/market_buyer", params={"limit": 1}, headers=self.headers
        )
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["transaction_count"], 0)
        self.assertIsNone(result["first_rated_at"])
        self.assertEqual(result["dismissed"][0]["event_id"], 10)

    def test_exhausted_pages_keep_full_summary_and_can_use_both_cursors(self) -> None:
        result = self.read(limit=1, active_cursor="a:7", dismissed_cursor="d:9")
        self.assertEqual(result["events"], [])
        self.assertEqual(result["dismissed"], [])
        self.assertEqual(result["total"], 7)
        self.assertEqual(result["dismissed_count"], 2)
        self.assertIsNone(result["pagination"]["next_active_cursor"])
        self.assertIsNone(result["pagination"]["next_dismissed_cursor"])

    def test_appends_and_dismissed_cursor_anchors_do_not_break_keyset_order(
        self,
    ) -> None:
        first = self.read(limit=2)
        with closing(self.connection()) as conn, conn:
            conn.execute(
                "INSERT INTO dismissals (event_id, dismissed_by, reason, timestamp) VALUES (2, 'operator', 'Resolved', '2026-01-04')"
            )
            conn.execute("""INSERT INTO rating_events
                (exchange_id, rater, rated_party, role, value, timestamp)
                VALUES ('new', 'z', 'Bob', 'market_seller', 4, '2026-01-04')""")
        result = self.read(
            limit=100, active_cursor=first["pagination"]["next_active_cursor"]
        )
        self.assertEqual(
            [row["event_id"] for row in result["events"]], [3, 4, 5, 6, 7, 12]
        )
        self.assertEqual(result["total"], 7)
        self.assertEqual(result["dismissed_count"], 3)

    def test_summary_and_pages_share_snapshot_during_committed_write(self) -> None:
        with closing(self.connection()) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
        database = self.path
        injected = []

        class InterleavedConnection(sqlite3.Connection):
            """Commit another connection after the first summary query starts."""

            def execute(self, sql, parameters=()):
                cursor = super().execute(sql, parameters)
                if sql.startswith("SELECT re.value") and not injected:
                    injected.append(True)
                    with closing(sqlite3.connect(database)) as writer, writer:
                        writer.execute("""INSERT INTO rating_events
                            (exchange_id, rater, rated_party, role, value, timestamp)
                            VALUES ('new', 'z', 'Bob', 'market_seller', 4, '2026-01-05')""")
                        writer.execute(
                            "INSERT INTO dismissals (event_id, dismissed_by, reason, timestamp) VALUES (1, 'operator', 'Resolved', '2026-01-05')"
                        )
                return cursor

        def reader(*_args, **_kwargs) -> sqlite3.Connection:
            conn = sqlite3.connect(database, factory=InterleavedConnection)
            conn.row_factory = sqlite3.Row
            return conn

        with patch.object(event_store, "get_connection", side_effect=reader):
            result = self.read(limit=2)
        self.assertTrue(injected, "Concurrent-write fixture did not run")
        self.assertEqual(result["distribution"]["-1"], 1)
        self.assertEqual(result["transaction_count"], 6)
        self.assertEqual(result["dismissed_count"], 2)
        self.assertEqual(result["last_rated_at"], "2026-01-03T00:00:00+00:00")
        self.assertEqual([row["event_id"] for row in result["events"]], [1, 2])
        fresh = self.read(limit=2)
        self.assertEqual(fresh["distribution"]["-1"], 0)
        self.assertEqual(fresh["dismissed_count"], 3)

    def test_large_history_materializes_only_bounded_pages(self) -> None:
        with closing(self.connection()) as conn, conn:
            conn.executemany(
                """INSERT INTO rating_events
                (exchange_id, rater, rated_party, role, value, comment, timestamp)
                VALUES (?, 'bulk', 'Bob', 'market_seller', 2, ?, '2026-02-01')""",
                ((f"bulk-{i}", "x" * 500) for i in range(20000)),
            )
            conn.executemany(
                """INSERT INTO rating_events
                (exchange_id, rater, rated_party, role, value, comment, timestamp)
                VALUES (?, 'bulk', 'Bob', 'market_seller', -1, ?, '2026-02-01')""",
                (
                    (f"dismissed-bulk-{i}", "Harm explanation " * 30)
                    for i in range(20000)
                ),
            )
            conn.execute("""INSERT INTO dismissals (event_id, dismissed_by, reason, timestamp)
                SELECT id, 'operator', 'Bad faith', '2026-03-01' FROM rating_events
                WHERE exchange_id LIKE 'dismissed-bulk-%'""")
        # Warm the HTTP client and worker before measuring the page request.
        self.read(limit=1)
        tracemalloc.start()
        try:
            result = self.read(limit=100)
            peak = tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
        self.assertEqual(len(result["events"]), 100)
        self.assertEqual(len(result["dismissed"]), 100)
        self.assertEqual(result["total"], 20007)
        self.assertEqual(result["distribution"]["2"], 20002)
        self.assertEqual(result["transaction_count"], 20006)
        self.assertEqual(result["dismissed_count"], 20002)
        self.assertLess(peak, 2_000_000, f"History page allocated {peak} Python bytes")


if __name__ == "__main__":
    unittest.main()
