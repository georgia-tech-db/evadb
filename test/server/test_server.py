# coding=utf-8
# Copyright 2018-2022 EVA
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

from eva.server.server import EvaServer

# Check for Python 3.8+ for IsolatedAsyncioTestCase support
if sys.version_info >= (3, 8):

    class ServerTests(unittest.IsolatedAsyncioTestCase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @patch("asyncio.start_server")
        async def test_server_functions(self, mock_start):
            eva_server = EvaServer()
            host = "localhost"
            port = 5432

            await eva_server.start_eva_server(host, port)

            # connection made
            client_reader1 = asyncio.StreamReader()
            client_writer1 = MagicMock()
            client_reader2 = asyncio.StreamReader()
            client_writer2 = MagicMock()

            # first client
            client_reader1.feed_data(b"SHOW UDFS;\n")
            client_reader1.feed_data(b"EXIT;\n")

            await eva_server.accept_client(client_reader1, client_writer1)
            assert len(eva_server._clients) == 1

            # another client
            client_reader2.feed_data(b"\xC4pple")  # trigger UnicodeDecodeError
            client_reader2.feed_eof()

            await eva_server.accept_client(client_reader2, client_writer2)
            assert len(eva_server._clients) == 2

            await eva_server.handle_client(client_reader2, client_writer2)

            await eva_server.stop_eva_server()
