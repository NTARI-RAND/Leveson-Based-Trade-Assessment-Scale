#!/usr/bin/env python3
"""Integration checks for SQLite initialization and API lifecycle.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0 or later.
"""

import asyncio
import json
import os
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

_TEMP = tempfile.TemporaryDirectory()
os.environ['LBTAS_DB_PATH'] = str(Path(_TEMP.name) / 'api.sqlite')
os.environ['LBTAS_API_KEY'] = 'test-key'

from api import event_store, main  # noqa: E402


async def request(method, path, body=None):
    """Send an ASGI HTTP request through the real application router."""
    sent = []
    payload = json.dumps(body).encode() if body is not None else b''
    received = False

    async def receive():
        nonlocal received
        if not received:
            received = True
            return {'type': 'http.request', 'body': payload, 'more_body': False}
        return {'type': 'http.disconnect'}

    async def send(message):
        sent.append(message)

    scope = {
        'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1',
        'method': method, 'scheme': 'http', 'path': path, 'raw_path': path.encode(),
        'query_string': b'', 'root_path': '', 'server': ('test', 80),
        'client': ('test', 1234), 'headers': [(b'content-type', b'application/json'),
                                              (b'x-api-key', b'test-key')],
    }
    await main.app(scope, receive, send)
    status = next(message['status'] for message in sent if message['type'] == 'http.response.start')
    data = b''.join(message.get('body', b'') for message in sent if message['type'] == 'http.response.body')
    return status, json.loads(data)


class InitializationTests(unittest.TestCase):
    def test_api_startup_initializes_schema_and_requests_do_not_run_ddl(self):
        """Reintroducing schema setup per request causes this trace check to fail."""
        statements = []
        connect = sqlite3.connect

        def traced_connect(*args, **kwargs):
            conn = connect(*args, **kwargs)
            conn.set_trace_callback(statements.append)
            return conn

        async def exercise():
            with patch.object(event_store.sqlite3, 'connect', side_effect=traced_connect):
                async with main.app.router.lifespan_context(main.app):
                    self.assertTrue(any(s.lstrip().upper().startswith('CREATE TABLE') for s in statements))
                    statements.clear()
                    status, _ = await request('POST', '/ratings', {
                        'exchange_id': 'exchange-1', 'rater': 'alice', 'rated_party': 'bob',
                        'role': 'seller', 'value': 2,
                    })
                    self.assertEqual(status, 201)
                    status, data = await request('GET', '/ratings/bob/seller')
                    self.assertEqual(status, 200)
                    self.assertEqual(data['total'], 1)
                    self.assertFalse(any(s.lstrip().upper().startswith(('CREATE TABLE', 'CREATE INDEX'))
                                         for s in statements), statements)
                async with main.app.router.lifespan_context(main.app):
                    status, data = await request('GET', '/ratings/bob/seller')
                    self.assertEqual(status, 200)
                    self.assertEqual(data['total'], 1)

        asyncio.run(exercise())

    def test_standalone_connections_initialize_independent_databases(self):
        """Dropping implicit initialization breaks existing standalone callers."""
        with tempfile.TemporaryDirectory() as directory:
            for path in (':memory:', str(Path(directory) / 'new.sqlite')):
                conn = event_store.get_connection(path)
                event_store.insert_event(conn, 'e', 'alice', 'bob', 'seller', None, 2, None, '2026-01-01')
                self.assertEqual(len(event_store.get_events_for_party_role(conn, 'bob', 'seller')), 1)
                conn.close()

    def test_concurrent_connections_preserve_writes(self):
        """Independent concurrent database connections must retain each event."""
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'concurrent.sqlite')
            event_store.get_connection(path).close()

            def write(index):
                conn = event_store.get_connection(path)
                try:
                    event_store.get_events_for_party_role(conn, 'bob', 'seller')
                    event_store.insert_event(conn, f'e-{index}', 'alice', 'bob', 'seller', None, 2, None, '2026-01-01')
                    rows = event_store.get_events_for_party_role(conn, 'bob', 'seller')
                    self.assertIn(f'e-{index}', [row['exchange_id'] for row in rows])
                finally:
                    conn.close()

            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(write, range(12)))
            conn = event_store.get_connection(path)
            try:
                self.assertEqual(len(event_store.get_events_for_party_role(conn, 'bob', 'seller')), 12)
            finally:
                conn.close()


if __name__ == '__main__':
    unittest.main()
