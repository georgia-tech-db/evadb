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
import threading
import time
import unittest
from unittest.mock import MagicMock

import mock
import pytest

from eva.server.server import EvaServer


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.stop_server_future = self.loop.create_future()
        asyncio.set_event_loop(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_server_protocol_connection_lost(self):
        socket_timeout = 65
        EvaServer.__connections__ = 0

        eva_server = EvaServer(socket_timeout)
        eva_server.transport = mock.Mock()
        eva_server.transport.close = MagicMock(return_value="closed")
        eva_server.transport.abort = MagicMock(return_value="aborted")

        # connection made
        eva_server.connection_made(eva_server.transport)
        self.assertEqual(EvaServer.__connections__, 1, "connection not made")

        time.sleep(1)

        # connection lost
        eva_server.connection_lost(None)
        self.assertEqual(EvaServer.__connections__, 0, "connection not lost")
        self.assertEqual(EvaServer.__errors__, 0, "connection not errored out")

        # connection made
        eva_server.connection_made(eva_server.transport)
        self.assertEqual(EvaServer.__connections__, 1, "connection not made")

        # connection lost with error
        eva_server.connection_lost(mock.Mock())
        self.assertEqual(EvaServer.__connections__, 0, "connection not lost")
        self.assertEqual(EvaServer.__errors__, 1, "connection not errored out")

    def test_server_protocol_data_received(self):
        socket_timeout = 60

        eva_server = EvaServer(socket_timeout)
        eva_server.transport = mock.Mock()
        eva_server.transport.close = MagicMock(return_value="closed")
        eva_server.transport.abort = MagicMock(return_value="aborted")

        quit_message = "quit"
        self.assertEqual(
            eva_server.data_received(quit_message), "closed", "transport not closed"
        )

        asyncio.set_event_loop(None)

        query_message = "query"
        with self.assertRaises(RuntimeError):
            # error due to lack of asyncio loop
            eva_server.data_received(query_message)

    @pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
    def test_server_integration_test(self):
        host = "0.0.0.0"
        port = 5489
        socket_timeout = 60

        def timeout_server():
            # need a more robust mechanism for when to cancel the future
            time.sleep(10)
            self.stop_server_future.cancel()

        thread = threading.Thread(target=timeout_server)
        thread.daemon = True
        thread.start()

        eva_server = EvaServer(socket_timeout)

        with self.assertRaises(SystemExit):
            eva_server.start_eva_server(host=host, port=port)
