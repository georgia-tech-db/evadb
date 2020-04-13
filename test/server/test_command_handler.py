# coding=utf-8
# Copyright 2018-2020 EVA
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

import unittest
import mock
import asyncio

from unittest.mock import MagicMock

from src.server.command_handler import handle_request
from src.utils.logging_manager import LoggingManager, LoggingLevel


class CommandHandlerTests(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.stop_server_future = self.loop.create_future()
        asyncio.set_event_loop(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_command_handler(self):
        transport = mock.Mock()
        transport.write = MagicMock(return_value="response_message")
        request_message = "INSERT INTO MyVideo (Frame_ID, Frame_Path) VALUES (2, '/mnt/frames/2.png');"

        task1 = self.loop.run_until_complete(handle_request(transport, request_message))

        output = task1.split('Row')[-1]
        self.assertEqual(output,"(Frame_ID=2, Frame_Path='/mnt/frames/2.png')")



if __name__ == '__main__':
    unittest.main()
