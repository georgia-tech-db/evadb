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
import os
import time
import signal
import threading
import mock

import asyncio

from unittest.mock import MagicMock

from src.server.server import start_server
from src.server.server import EvaServer


class ServerTests(unittest.TestCase):
            
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_server(self):

        pid = os.getpid()

        def trigger_signal():
            # need a more robust mechanism for when to send the signal
            time.sleep(1)
            os.kill(pid, signal.SIGINT)

        thread = threading.Thread(target=trigger_signal)
        thread.daemon = True
        thread.start()

        with self.assertRaises(SystemExit):
            start_server(host="localhost", port=5432, loop=self.loop)

    def test_server_protocol(self):

        eva_server = EvaServer()
        eva_server.transport = mock.Mock()
        eva_server.transport.close = MagicMock(return_value="closed")
        eva_server.transport.abort = MagicMock(return_value="aborted")

        # connection made
        eva_server.connection_made(eva_server.transport)
        self.assertEqual(EvaServer.__connections__, 1,
                         "connection not made")

        # connection lost
        eva_server.connection_lost(exc=None)
        self.assertEqual(EvaServer.__connections__, 0,
                         "connection not lost")
        self.assertEqual(EvaServer.__errors__, 0,
                         "connection not errored out")

        # connection made
        eva_server.connection_made(eva_server.transport)
        self.assertEqual(EvaServer.__connections__, 1,
                         "connection not made")

        # connection lost with error
        eva_server.connection_lost(exc=mock.Mock())
        self.assertEqual(EvaServer.__connections__, 0,
                         "connection not lost")
        self.assertEqual(EvaServer.__errors__, 1,
                         "connection not errored out")

        # data received
        data = mock.Mock()
        data.decode = MagicMock(return_value="quit")
        self.assertEqual(eva_server.data_received(data), "closed",
                         "transport not closed")

        asyncio.set_event_loop(None)

        with self.assertRaises(RuntimeError):
            data.decode = MagicMock(return_value="query")
            # error due to lack of asyncio loop
            eva_server.data_received(data)


if __name__ == '__main__':
    unittest.main()
