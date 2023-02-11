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
import unittest

from mock import MagicMock, patch

from eva.server.interpreter import start_cmd_client


class InterpreterTests(unittest.IsolatedAsyncioTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @patch("asyncio.open_connection")
    @patch("eva.server.interpreter.create_stdin_reader")
    async def test_start_cmd_client(self, mock_stdin_reader, mock_open):
        host = "localhost"
        port = 5432

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

        # with self.assertRaises(Exception):
        await start_cmd_client(host, port)

    @patch("asyncio.wait")
    async def test_exception_in_start_cmd_client(self, mock_wait):
        host = "localhost"
        port = 5432
        mock_wait.side_effect = Exception("Test")

        with self.assertRaises(Exception):
            await start_cmd_client(host, port)
