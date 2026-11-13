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
        self.client = self.enterContext(TestClient(app))
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
        return self.connect(self.path, **kwargs)

    def read(self, **params) -> dict:
        """Read through the mounted HTTP route, including query validation."""
        response = self.client.get(self.url, params=params, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        if "limit" in params:
            self.assertIn("pagination", response.json())
        return response.json()

    def test_complete_harm_index_ignores_page_and_cursors(self):
        """Dropping off-page harm/dismissals, duplicating -1s or leaking scope fails."""
        with closing(self.connection()) as conn, conn:
            conn.execute("""INSERT INTO rating_events
                (id, exchange_id, rater, rated_party, role, value, comment, timestamp)
                VALUES (12, 'newest-harm', 'z', 'Bob', 'market_seller', -1,
                        'Accountable harm', '2026-02-01')""")
            conn.execute("""INSERT INTO dismissals
                (event_id, dismissed_by, reason, timestamp)
                VALUES (7, 'operator', 'Forgiven', '2026-02-02')""")
            conn.execute("""INSERT INTO contests
                (event_id, contested_by, reason, timestamp)
                VALUES (1, 'Bob', 'Review pending', '2026-02-02')""")
            conn.execute("""INSERT INTO contests
                (event_id, contested_by, reason, timestamp)
                VALUES (9, 'Bob', 'Disputed', '2026-01-02')""")
            conn.execute("""INSERT INTO upholds
                (event_id, upheld_by, reason, timestamp)
                VALUES (9, 'operator', 'Checked', '2026-01-03')""")
        expected = [
            {
                "event_id": 12,
                "exchange_id": "newest-harm",
                "rated_at": "2026-02-01",
                "value": -1,
                "state": "active",
                "contested": False,
                "upheld": False,
            },
            {
                "event_id": 7,
                "exchange_id": "seventh",
                "rated_at": "2026-01-03T00:00:00+00:00",
                "value": 2,
                "state": "dismissed",
                "contested": False,
                "upheld": False,
                "dismissed_by": "operator",
                "reason": "Forgiven",
                "dismissed_at": "2026-02-02",
            },
            {
                "event_id": 9,
                "exchange_id": "dismissed-two",
                "rated_at": "2026-01-01T00:00:00+00:00",
                "value": -1,
                "state": "dismissed",
                "contested": True,
                "upheld": True,
                "dismissed_by": "operator",
                "reason": "Bad faith",
                "dismissed_at": "2026-01-04",
            },
            {
                "event_id": 8,
                "exchange_id": "dismissed-one",
                "rated_at": "2026-01-01T00:00:00+00:00",
                "value": -1,
                "state": "dismissed",
                "contested": False,
                "upheld": False,
                "dismissed_by": "operator",
                "reason": "Bad faith",
                "dismissed_at": "2026-01-04",
            },
            {
                "event_id": 1,
                "exchange_id": "shared",
                "rated_at": "2026-01-01T00:00:00+00:00",
                "value": -1,
                "state": "active",
                "contested": True,
                "upheld": False,
            },
        ]
        for params in (
            {},
            {"limit": 1},
            {"limit": 1, "active_cursor": "a:12", "dismissed_cursor": "d:7"},
        ):
            with self.subTest(params=params):
                result = self.read(**params)
                self.assertIn("harm_index", result)
                self.assertEqual(result["harm_index"], expected)
                self.assertEqual(
                    result["dismissed_distribution"],
                    {"-1": 2, "0": 0, "1": 0, "2": 1, "3": 0, "4": 0},
                )
                self.assertEqual(result["dismissed_count"], 3)
                if params == {"limit": 1}:
                    self.assertEqual([r["event_id"] for r in result["events"]], [1])
                    self.assertEqual([r["event_id"] for r in result["dismissed"]], [8])

    def test_dismissed_distribution_keeps_every_level_separate(self):
        """Pooling dismissal levels or including another role/party must fail."""
        with closing(self.connection()) as conn, conn:
            conn.executemany(
                """INSERT INTO dismissals
                (event_id, dismissed_by, reason, timestamp)
                VALUES (?, 'operator', 'Resolved', '2026-02-02')""",
                [(i,) for i in (1, 2, 3, 4, 5, 6)],
            )
        for params in ({}, {"limit": 1}):
            result = self.read(**params)
            self.assertIn("dismissed_distribution", result)
            self.assertEqual(
                result["dismissed_distribution"],
                {"-1": 3, "0": 1, "1": 1, "2": 1, "3": 1, "4": 1},
            )
            self.assertEqual(result["dismissed_count"], 8)
            self.assertEqual(len(result["harm_index"]), 8)

    def test_clean_history_has_empty_index_and_zero_dismissed_levels(self):
        """Clean history must not acquire another scope's harm or missing levels."""
        self.url = "/ratings/Clean/market_seller"
        with closing(self.connection()) as conn, conn:
            conn.execute("""INSERT INTO rating_events
                (exchange_id, rater, rated_party, role, value, timestamp)
                VALUES ('clean', 'a', 'Clean', 'market_seller', 4, '2026-02-01')""")
        for params in ({}, {"limit": 1}):
            result = self.read(**params)
            self.assertIn("harm_index", result)
            self.assertEqual(result["harm_index"], [])
            self.assertEqual(
                result["dismissed_distribution"],
                {"-1": 0, "0": 0, "1": 0, "2": 0, "3": 0, "4": 0},
            )

    def test_fixture_supports_real_application_lifespan(self):
        """Startup's positional database path must not conflict with fixture path."""
        try:
            with TestClient(app) as client:
                response = client.get(
                    self.url, params={"limit": 1}, headers=self.headers
                )
                self.assertEqual(response.status_code, 200, response.text)
        except TypeError as error:
            self.fail(f"Fixture cannot enter application lifespan: {error}")

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
            conn.execute(
                "INSERT INTO contests (event_id, contested_by, reason, timestamp) VALUES (3, 'Bob', 'Pending review', '2026-01-02')"
            )
        for params in ({}, {"limit": 7}):
            row = self.read(**params)["events"][2]
            self.assertEqual(
                row,
                {
                    "event_id": 3,
                    "value": 1,
                    "category": None,
                    "comment": "Local explanation",
                    "exchange_id": "third",
                    "rater": "c",
                    "rated_at": "2026-01-01T00:00:00+00:00",
                    "defaulted": False,
                    "contested": True,
                    "contested_by": "Bob",
                    "contest_reason": "Pending review",
                    "contested_at": "2026-01-02",
                    "upheld": False,
                },
            )

    def test_unpaged_response_retains_existing_contract(self) -> None:
        """Catch dropped or renamed root, event, timeout and annotation fields."""
        events = []
        for event_id, value, exchange, rater in (
            (1, -1, "shared", "a"),
            (2, 0, "shared", "b"),
            (3, 1, "third", "c"),
            (4, 2, "fourth", "system"),
            (5, 3, "fifth", "e"),
            (6, 4, "sixth", "f"),
            (7, 2, "seventh", "g"),
        ):
            events.append(
                {
                    "event_id": event_id,
                    "value": value,
                    "exchange_id": exchange,
                    "rater": rater,
                    "category": None,
                    "comment": "Local explanation",
                    "rated_at": "2026-01-03T00:00:00+00:00"
                    if event_id == 7
                    else "2026-01-01T00:00:00+00:00",
                    "defaulted": event_id == 4,
                    "contested": event_id == 5,
                }
            )
        events[4].update(
            contested_by="Bob",
            contest_reason="Disputed",
            contested_at="2026-01-02",
            upheld=True,
            upheld_by="operator",
            uphold_reason="Evidence checked",
            upheld_at="2026-01-03",
        )
        dismissed = [
            {
                "event_id": event_id,
                "value": -1,
                "exchange_id": exchange,
                "rater": rater,
                "category": None,
                "comment": "Local explanation",
                "rated_at": "2026-01-01T00:00:00+00:00",
                "dismissed_by": "operator",
                "reason": "Bad faith",
                "dismissed_at": "2026-01-04",
            }
            for event_id, exchange, rater in [
                (8, "dismissed-one", "h"),
                (9, "dismissed-two", "i"),
            ]
        ]
        self.assertEqual(
            self.read(),
            {
                "rated_party": "Bob",
                "role": "market_seller",
                "distribution": {"-1": 1, "0": 1, "1": 1, "2": 2, "3": 1, "4": 1},
                "total": 7,
                "transaction_count": 6,
                "first_rated_at": "2026-01-01T00:00:00+00:00",
                "last_rated_at": "2026-01-03T00:00:00+00:00",
                "defaulted_count": 1,
                "dismissed_count": 2,
                "dismissed_distribution": {
                    "-1": 2,
                    "0": 0,
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                },
                "harm_index": [
                    {
                        "event_id": 9,
                        "value": -1,
                        "exchange_id": "dismissed-two",
                        "rated_at": "2026-01-01T00:00:00+00:00",
                        "state": "dismissed",
                        "contested": False,
                        "upheld": False,
                        "dismissed_by": "operator",
                        "reason": "Bad faith",
                        "dismissed_at": "2026-01-04",
                    },
                    {
                        "event_id": 8,
                        "value": -1,
                        "exchange_id": "dismissed-one",
                        "rated_at": "2026-01-01T00:00:00+00:00",
                        "state": "dismissed",
                        "contested": False,
                        "upheld": False,
                        "dismissed_by": "operator",
                        "reason": "Bad faith",
                        "dismissed_at": "2026-01-04",
                    },
                    {
                        "event_id": 1,
                        "value": -1,
                        "exchange_id": "shared",
                        "rated_at": "2026-01-01T00:00:00+00:00",
                        "state": "active",
                        "contested": False,
                        "upheld": False,
                    },
                ],
                "events": events,
                "dismissed": dismissed,
            },
        )

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
                response = self.client.get(
                    self.url, params=params, headers=self.headers
                )
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
        self.assertEqual([row["event_id"] for row in result["harm_index"]], [9, 8, 1])
        fresh = self.read(limit=2)
        self.assertEqual(fresh["distribution"]["-1"], 0)
        self.assertEqual(fresh["dismissed_count"], 3)

    def test_unpaged_summary_and_index_share_snapshot_during_committed_write(
        self,
    ) -> None:
        with closing(self.connection()) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
        database = self.path
        injected = []

        class InterleavedConnection(sqlite3.Connection):
            """Commit another connection after the first summary query starts."""

            def execute(self, sql, parameters=()):
                cursor = super().execute(sql, parameters)
                if sql.lstrip().startswith("SELECT") and not injected:
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
            result = self.read()
        self.assertTrue(injected, "Concurrent-write fixture did not run")
        self.assertEqual(result["distribution"]["-1"], 1)
        self.assertEqual(result["transaction_count"], 6)
        self.assertEqual(result["dismissed_count"], 2)
        self.assertEqual(result["last_rated_at"], "2026-01-03T00:00:00+00:00")
        self.assertEqual([row["event_id"] for row in result["events"][:2]], [1, 2])
        self.assertEqual([row["event_id"] for row in result["harm_index"]], [9, 8, 1])
        fresh = self.read()
        self.assertEqual(fresh["distribution"]["-1"], 0)
        self.assertEqual(fresh["dismissed_count"], 3)

    def test_late_timestamp_commit_requires_a_fresh_traversal(self):
        """A fresh traversal recovers a late commit behind an issued cursor."""
        first = self.read(limit=2)
        with closing(self.connection()) as conn, conn:
            conn.execute("""INSERT INTO rating_events
                (id, exchange_id, rater, rated_party, role, value, timestamp)
                VALUES (12, 'late', 'z', 'Bob', 'market_seller', 4, '2025-12-31')""")
        continued = self.read(
            limit=100, active_cursor=first["pagination"]["next_active_cursor"]
        )
        self.assertEqual(
            [row["event_id"] for row in continued["events"]], [3, 4, 5, 6, 7]
        )
        self.assertEqual(
            [row["event_id"] for row in self.read(limit=100)["events"]],
            [12, 1, 2, 3, 4, 5, 6, 7],
        )

    def test_deep_cursor_page_seeks_past_preceding_rows(self):
        """A cursor page must not scan all earlier events in its partition."""
        from api.history import HistoryQuery, _page

        with closing(self.connection()) as conn, conn:
            conn.executemany(
                """INSERT INTO rating_events
                (id, exchange_id, rater, rated_party, role, value, timestamp)
                VALUES (?, ?, 'bulk', 'Bob', 'market_seller', 2, '2026-02-01')""",
                ((i, f"seek-{i}") for i in range(12, 10012)),
            )
            steps = []
            conn.set_progress_handler(lambda: steps.append(1) and 0, 100)
            rows, cursor = _page(
                conn, HistoryQuery("Bob", "market_seller", 2), "a:10009", "a"
            )
            conn.set_progress_handler(None, 0)
        self.assertEqual([row["event_id"] for row in rows], [10010, 10011])
        self.assertIsNone(cursor)
        self.assertLess(len(steps), 20, "Cursor page scanned the preceding history")

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
        # The mandatory complete harm index scales with harm/dismissal count.
        # Measure only narrative pages; never weaken their original 2 MB bound.
        from api.history import HistoryQuery, _page

        with closing(self.connection()) as conn:
            tracemalloc.start()
            try:
                query = HistoryQuery("Bob", "market_seller", 100)
                active, _ = _page(conn, query, None, "a")
                dismissed, _ = _page(conn, query, None, "d")
                peak = tracemalloc.get_traced_memory()[1]
            finally:
                tracemalloc.stop()
        self.assertEqual(len(active), 100)
        self.assertEqual(len(dismissed), 100)
        result = self.read(limit=100)
        self.assertEqual(len(result["harm_index"]), 20003)
        self.assertEqual(
            result["dismissed_distribution"],
            {"-1": 20002, "0": 0, "1": 0, "2": 0, "3": 0, "4": 0},
        )
        self.assertEqual(len(result["events"]), 100)
        self.assertEqual(len(result["dismissed"]), 100)
        self.assertEqual(result["total"], 20007)
        self.assertEqual(result["distribution"]["2"], 20002)
        self.assertEqual(result["transaction_count"], 20006)
        self.assertEqual(result["dismissed_count"], 20002)
        self.assertLess(peak, 2_000_000, f"History page allocated {peak} Python bytes")


if __name__ == "__main__":
    unittest.main()
