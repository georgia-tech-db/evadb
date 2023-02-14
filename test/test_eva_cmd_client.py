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

from mock import patch

# Check for Python 3.8+ for IsolatedAsyncioTestCase support
if sys.version_info >= (3, 8):

    class CMDClientTest(unittest.IsolatedAsyncioTestCase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def get_mock_stdin_reader(self) -> asyncio.StreamReader:
            stdin_reader = asyncio.StreamReader()
            stdin_reader.feed_data(b"EXIT;\n")
            stdin_reader.feed_eof()
            return stdin_reader

        @patch("eva.server.interpreter.create_stdin_reader")
        @patch("eva.server.interpreter.start_cmd_client")
        async def test_eva_client(self, mock_client, mock_stdin_reader):
            # Must import after patching start_cmd_client
            from eva.eva_cmd_client import eva_client

            mock_stdin_reader.return_value = self.get_mock_stdin_reader()
            mock_client.side_effect = Exception("Test")

            with self.assertRaises(Exception):
                await eva_client()

            mock_client.reset_mock()
            mock_client.side_effect = KeyboardInterrupt

            # Pass exception
            await eva_client()
