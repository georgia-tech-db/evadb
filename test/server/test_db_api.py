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
import sys
import unittest
from unittest.mock import AsyncMock

from eva.models.server.response import Response
from eva.server.db_api import EVACursor, connect

# Check for Python 3.8+ for IsolatedAsyncioTestCase support
if sys.version_info >= (3, 8):

    class DBAPITests(unittest.IsolatedAsyncioTestCase):
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

            # concurrent queries not allowed
            with self.assertRaises(SystemError):
                asyncio.run(eva_cursor.execute_async(query))

        def test_eva_cursor_fetch_one_async(self):
            connection = AsyncMock()
            eva_cursor = EVACursor(connection)
            message = "test_response"
            serialized_message = Response.serialize("test_response")
            serialized_message_length = b"%d" % len(serialized_message)
            connection._reader.readline.side_effect = [serialized_message_length]
            connection._reader.readexactly.side_effect = [serialized_message]
            response = asyncio.run(eva_cursor.fetch_one_async())
            self.assertEqual(eva_cursor._pending_query, False)
            self.assertEqual(message, response)

        def test_eva_cursor_fetch_one_sync(self):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            connection = AsyncMock()
            eva_cursor = EVACursor(connection)

            message = "test_response"
            serialized_message = Response.serialize("test_response")
            serialized_message_length = b"%d" % len(serialized_message)
            connection._reader.readline.side_effect = [serialized_message_length]
            connection._reader.readexactly.side_effect = [serialized_message]

            response = eva_cursor.fetch_one()
            self.assertEqual(eva_cursor._pending_query, False)
            self.assertEqual(message, response)

        def test_eva_connection(self):
            hostname = "localhost"

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            connection = AsyncMock()
            eva_cursor = EVACursor(connection)

            # test upload transformation with existing file
            eva_cursor._upload_transformation('UPLOAD PATH "upload.txt" BLOB')

            # test upload transformation with non-existing file
            with self.assertRaises(FileNotFoundError):
                eva_cursor._upload_transformation('UPLOAD PATH "blah.txt" BLOB')

            # test attr
            with self.assertRaises(AttributeError):
                eva_cursor.__getattr__("foo")

            # test connection error with incorrect port
            with self.assertRaises(OSError):
                connect(hostname, port=1)

        async def test_eva_signal(self):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            connection = AsyncMock()
            eva_cursor = EVACursor(connection)

            query = "test_query"
            await eva_cursor.execute_async(query)

        def test_client_stop_query(self):
            connection = AsyncMock()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            connection.protocol.loop = loop

            eva_cursor = EVACursor(connection)
            eva_cursor.execute("test_query")
            eva_cursor.stop_query()
            self.assertEqual(eva_cursor._pending_query, False)

        def test_get_attr(self):
            connection = AsyncMock()

            eva_cursor = EVACursor(connection)
            with self.assertRaises(AttributeError):
                eva_cursor.missing_function()
