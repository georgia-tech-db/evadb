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

from mock import MagicMock, patch

from evadb.configuration.constants import EvaDB_DATABASE_DIR
from evadb.server.server import EvaServer

# Check for Python 3.8+ for IsolatedAsyncioTestCase support
if sys.version_info >= (3, 8):

    class ServerTests(unittest.IsolatedAsyncioTestCase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @patch("asyncio.start_server")
        async def test_server_functions(self, mock_start):
            evadb_server = EvaServer()
            host = "localhost"
            port = 8803

            await evadb_server.start_evadb_server(EvaDB_DATABASE_DIR, host, port)

            # connection made
            client_reader1 = asyncio.StreamReader()
            client_writer1 = MagicMock()
            client_reader2 = asyncio.StreamReader()
            client_writer2 = MagicMock()

            # first client
            client_reader1.feed_data(b"SHOW UDFS;\n")
            client_reader1.feed_data(b"EXIT;\n")

            await evadb_server.accept_client(client_reader1, client_writer1)
            assert len(evadb_server._clients) == 1

            # another client
            client_reader2.feed_data(b"\xC4pple")  # trigger UnicodeDecodeError
            client_reader2.feed_eof()

            await evadb_server.accept_client(client_reader2, client_writer2)
            assert len(evadb_server._clients) == 2

            await evadb_server.handle_client(client_reader2, client_writer2)

            await evadb_server.stop_evadb_server()
