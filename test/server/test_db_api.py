# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import asyncio
import os
import sys
import unittest
from test.util import suffix_pytest_xdist_worker_id_to_dir

from mock import MagicMock, patch

from evadb.interfaces.relational.db import EvaDBCursor, connect_remote
from evadb.models.server.response import Response

# Check for Python 3.8+ for IsolatedAsyncioTestCase support
if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock

    class DBAPITests(unittest.IsolatedAsyncioTestCase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def setUp(self) -> None:
            print("setUp")
            f = open(suffix_pytest_xdist_worker_id_to_dir("upload.txt"), "w")
            f.write("dummy data")
            f.close()
            return super().setUp()

        def tearDown(self) -> None:
            print("tearDown")
            os.remove(suffix_pytest_xdist_worker_id_to_dir("upload.txt"))
            return super().tearDown()

        def test_evadb_cursor_execute_async(self):
            connection = AsyncMock()
            evadb_cursor = EvaDBCursor(connection)
            query = "test_query"
            asyncio.run(evadb_cursor.execute_async(query))
            self.assertEqual(evadb_cursor._pending_query, True)

            # concurrent queries not allowed
            with self.assertRaises(SystemError):
                asyncio.run(evadb_cursor.execute_async(query))

        def test_evadb_cursor_fetch_all_async(self):
            connection = AsyncMock()
            evadb_cursor = EvaDBCursor(connection)
            message = "test_response"
            serialized_message = Response.serialize("test_response")
            serialized_message_length = b"%d" % len(serialized_message)
            connection._reader.readline.side_effect = [serialized_message_length]
            connection._reader.readexactly.side_effect = [serialized_message]
            response = asyncio.run(evadb_cursor.fetch_all_async())
            self.assertEqual(evadb_cursor._pending_query, False)
            self.assertEqual(message, response)

        def test_evadb_cursor_fetch_one_sync(self):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            connection = AsyncMock()
            evadb_cursor = EvaDBCursor(connection)

            message = "test_response"
            serialized_message = Response.serialize("test_response")
            serialized_message_length = b"%d" % len(serialized_message)
            connection._reader.readline.side_effect = [serialized_message_length]
            connection._reader.readexactly.side_effect = [serialized_message]

            response = evadb_cursor.fetch_one()
            self.assertEqual(evadb_cursor._pending_query, False)
            self.assertEqual(message, response)

        def test_evadb_connection(self):
            hostname = "localhost"

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            connection = AsyncMock()
            evadb_cursor = EvaDBCursor(connection)

            # test attr
            with self.assertRaises(AttributeError):
                evadb_cursor.__getattr__("foo")

            # test connection error with incorrect port
            with self.assertRaises(OSError):
                connect_remote(hostname, port=1)

        async def test_evadb_signal(self):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            connection = AsyncMock()
            evadb_cursor = EvaDBCursor(connection)

            query = "test_query"
            await evadb_cursor.execute_async(query)

        def test_client_stop_query(self):
            connection = AsyncMock()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            connection.protocol.loop = loop

            evadb_cursor = EvaDBCursor(connection)
            evadb_cursor.execute("test_query")
            evadb_cursor.stop_query()
            self.assertEqual(evadb_cursor._pending_query, False)

        def test_get_attr(self):
            connection = AsyncMock()

            evadb_cursor = EvaDBCursor(connection)
            with self.assertRaises(AttributeError):
                evadb_cursor.missing_function()

        @patch("asyncio.open_connection")
        def test_get_connection(self, mock_open):
            server_reader = asyncio.StreamReader()
            server_writer = MagicMock()
            mock_open.return_value = (server_reader, server_writer)

            connection = connect_remote("localhost", port=1)

            self.assertNotEqual(connection, None)
