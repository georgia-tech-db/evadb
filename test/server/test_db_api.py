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

from eva.server.db_api import EVACursor
from eva.models.server.response import Response


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


class DBAPITests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_EVA_Cursor_execute_async(self):
        protocol = AsyncMock()
        eva_cursor = EVACursor(protocol)
        query = "test_query"
        asyncio.run(eva_cursor.execute_async(query))
        self.assertEqual(eva_cursor._pending_query, True)
        protocol.send_message.assert_called_with(query)

        # concurrent queries not allowed
        with self.assertRaises(SystemError):
            asyncio.run(eva_cursor.execute_async(query))

    @mock.patch.object(Response, 'from_json')
    def test_eva_cursor_fetch_one_async(self, mock_response):
        protocol = AsyncMock()
        eva_cursor = EVACursor(protocol)
        response = "test_response"
        mock_response.side_effect = [response]
        expected = asyncio.run(eva_cursor.fetch_one_async())
        self.assertEqual(eva_cursor._pending_query, False)
        protocol.queue.get.assert_called_once()
        self.assertEqual(expected, response)
