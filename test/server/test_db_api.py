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
import os
import signal
import socket
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import MagicMock

import mock

from eva.models.server.response import Response
from eva.server.async_protocol import EvaClient
from eva.server.db_api import EVACursor, connect


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    address, port = s.getsockname()
    s.close()
    return port


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


class DBAPITests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self) -> None:
        f = open("upload.txt", "w")
        f.write("dummy data")
        f.close()
        return super().setUp()

    def tearDown(self) -> None:
        os.remove("upload.txt")
        return super().tearDown()

    def test_eva_cursor_execute_async(self):
        connection = AsyncMock()
        eva_cursor = EVACursor(connection)
        query = "test_query"
        asyncio.run(eva_cursor.execute_async(query))
        self.assertEqual(eva_cursor._pending_query, True)
        connection.protocol.send_message.assert_called_with(query)

        # concurrent queries not allowed
        with self.assertRaises(SystemError):
            asyncio.run(eva_cursor.execute_async(query))

    @mock.patch.object(Response, "deserialize")
    def test_eva_cursor_fetch_one_async(self, mock_response):
        connection = AsyncMock()
        eva_cursor = EVACursor(connection)
        response = "test_response"
        mock_response.side_effect = [response]
        expected = asyncio.run(eva_cursor.fetch_one_async())
        self.assertEqual(eva_cursor._pending_query, False)
        connection.protocol.queue.get.assert_called_once()
        self.assertEqual(expected, response)

    @mock.patch.object(Response, "deserialize")
    def test_eva_cursor_fetch_one_sync(self, mock_response):
        connection = AsyncMock()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        connection.protocol.loop = loop

        eva_cursor = EVACursor(connection)
        response = "test_response"
        mock_response.side_effect = [response]
        expected = eva_cursor.fetch_one()
        self.assertEqual(eva_cursor._pending_query, False)
        connection.protocol.queue.get.assert_called_once()
        self.assertEqual(expected, response)

    def test_eva_connection(self):
        hostname = "localhost"

        mock_server_port = get_free_port()
        mock_server = HTTPServer((hostname, mock_server_port), BaseHTTPRequestHandler)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        connection = connect(hostname, mock_server.server_port)
        cursor = connection.cursor()

        self.assertEquals(type(connection._protocol), EvaClient)
        self.assertEquals(type(cursor), EVACursor)

        # test upload transformation with existing file
        cursor._upload_transformation('UPLOAD PATH "upload.txt" BLOB')

        # test upload transformation with non-existing file
        with self.assertRaises(FileNotFoundError):
            cursor._upload_transformation('UPLOAD PATH "blah.txt" BLOB')

        # test attr
        with self.assertRaises(AttributeError):
            cursor.__getattr__("foo")

        # test connection error with incorrect port
        with self.assertRaises(OSError):
            connect(hostname, port=1)

    def test_eva_signal(self):
        hostname = "localhost"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        mock_server_port = get_free_port()
        mock_server = HTTPServer((hostname, mock_server_port), BaseHTTPRequestHandler)

        connection = connect(hostname, mock_server.server_port)
        cursor = connection.cursor()

        def trigger_signal():
            time.sleep(1)
            os.kill(os.getpid(), signal.SIGTERM)

        thread = threading.Thread(target=trigger_signal)
        thread.daemon = True
        thread.start()

        query = "test_query"
        cursor.execute(query)
