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
import sys
import unittest
from test.util import find_free_port

from mock import MagicMock, patch

from evadb.server.interpreter import create_stdin_reader, start_cmd_client

# Check for Python 3.8+ for IsolatedAsyncioTestCase support
if sys.version_info >= (3, 8):

    class InterpreterTests(unittest.IsolatedAsyncioTestCase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @patch("asyncio.open_connection")
        @patch("evadb.server.interpreter.create_stdin_reader")
        @patch("evadb.interfaces.relational.db.EvaDBCursor.execute_async")
        @patch("evadb.interfaces.relational.db.EvaDBCursor.fetch_all_async")
        async def test_start_cmd_client(
            self, mock_fetch, mock_execute, mock_stdin_reader, mock_open
        ):
            host = "localhost"
            port = find_free_port()

            server_reader = asyncio.StreamReader()
            server_writer = MagicMock()

            server_reader.feed_data(b"SHOW UDFS;\n")
            server_reader.feed_data(b"EXIT;\n")

            mock_open.return_value = (server_reader, server_writer)

            stdin_reader = asyncio.StreamReader()
            stdin_reader.feed_data(b"SHOW UDFS;\n")
            stdin_reader.feed_data(b"EXIT;\n")
            stdin_reader.feed_eof()

            mock_stdin_reader.return_value = stdin_reader

            await start_cmd_client(host, port)

        @patch("asyncio.open_connection")
        async def test_exception_in_start_cmd_client(self, mock_open):
            mock_open.side_effect = Exception("open")

            await start_cmd_client(MagicMock(), MagicMock())

        @patch("asyncio.events.AbstractEventLoop.connect_read_pipe")
        async def test_create_stdin_reader(self, mock_read_pipe):
            sys.stdin = MagicMock()

            try:
                stdin_reader = await create_stdin_reader()
                self.assertNotEqual(stdin_reader, None)
            except Exception:
                pass
