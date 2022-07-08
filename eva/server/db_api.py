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
import asyncio
import random
import base64
import os

from eva.server.async_protocol import EvaClient
from eva.models.server.response import Response


class EVAConnection:
    def __init__(self, transport, protocol):
        self._transport = transport
        self._protocol = protocol

    def cursor(self):
        return EVACursor(self._protocol)

    @property
    def protocol(self):
        return self._protocol


class EVACursor(object):

    def __init__(self, protocol):
        self._protocol = protocol
        self._pending_query = False

    async def execute_async(self, query: str):
        """
        Send query to the EVA server.
        """
        if self._pending_query:
            raise SystemError(
                'EVA does not support concurrent queries. \
                    Call fetch_all() to complete the pending query')
        query = self._upload_transformation(query)
        await self._protocol.send_message(query)
        self._pending_query = True

    async def fetch_one_async(self) -> Response:
        """
        fetch_one returns one batch instead of one row for now.
        """
        try:
            message = await self._protocol.queue.get()
            response = await asyncio.coroutine(Response.from_json)(message)
        except Exception as e:
            raise e
        self._pending_query = False
        return response

    async def fetch_all_async(self) -> Response:
        """
        fetch_all is the same as fetch_one for now.
        """
        return await self.fetch_one_async()

    def _upload_transformation(self, query: str) -> str:
        """
        Special case:
         - UPLOAD: the client read the file and uses base64 to encode
         the content into a string.
        """
        if 'UPLOAD' in query:
            query_list = query.split()
            file_path = query_list[2][1:-1]
            dst_path = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                bytes_read = f.read()
                b64_string = str(base64.b64encode(bytes_read))
                query = 'UPLOAD PATH ' + \
                        '\'' + dst_path + '\'' + \
                        ' BLOB ' + \
                        '\"' + b64_string + '\" ';

                for token in query_list[3:]:
                    query += token + ' '

        return query

    def __getattr__(self, name):
        """
        Auto generate sync function calls from async
        Sync function calls should not be used in an async environment.
        """
        func = object.__getattribute__(self, '%s_async' % name)
        if not asyncio.iscoroutinefunction(func):
            raise AttributeError

        def func_sync(*args, **kwargs):
            loop = self._protocol.loop
            res = loop.run_until_complete(func(*args, **kwargs))
            return res

        return func_sync


async def connect_async(host: str, port: int,
                        max_retry_count: int = 3, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    retries = max_retry_count * [1]

    while True:
        try:
            transport, protocol = await \
                loop.create_connection(lambda: EvaClient(loop), host, port)

        except Exception as e:
            if not retries:
                raise e
            await asyncio.sleep(retries.pop(0) - random.random())
        else:
            break

    return EVAConnection(transport, protocol)


def connect(host: str, port: int, max_retry_count: int = 3):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(connect_async(host, port, max_retry_count))
