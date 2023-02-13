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
import sys
import unittest

import mock

# Check for Python 3.8+ for IsolatedAsyncioTestCase support
if sys.version_info >= (3, 8):

    class CMDClientTest(unittest.IsolatedAsyncioTestCase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @mock.patch("eva.eva_cmd_client.eva_client")
        def test_main(self, mock_client):
            from eva.eva_cmd_client import main

            with mock.patch.object(sys, "argv", ["test"]):
                main()
            mock_client.assert_called_once_with(host="0.0.0.0", port=5432)

        def test_parse_args(self):
            from eva.eva_cmd_client import parse_args

            args = parse_args(["-P", "2345", "-H", "test"])
            self.assertEqual(args.host, "test")
            self.assertEqual(args.port, 2345)

        @mock.patch("eva.server.interpreter.start_cmd_client")
        def test_eva_client(self, mock_client):
            from eva.eva_cmd_client import eva_client

            eva_client()
            mock_client.assert_called_once()

        @mock.patch("eva.server.interpreter.start_cmd_client")
        async def test_exception_in_eva_client(self, mock_client):
            from eva.eva_cmd_client import eva_client

            mock_client.side_effect = Exception("Test")
            with self.assertRaises(Exception):
                await eva_client()

            mock_client.side_effect = KeyboardInterrupt
            # Pass exception
            await eva_client()
