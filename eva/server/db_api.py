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
import base64
import os
import random
from signal import SIGINT, SIGTERM

from eva.models.server.response import Response
from eva.server.async_protocol import EvaClient


class EVAConnection:
    def __init__(self, transport, protocol):
        self._transport = transport
        self._protocol = protocol
        self._cursor = None

    def cursor(self):
        # Unqiue cursor for every connection
        if self._cursor is None:
            self._cursor = EVACursor(self)
        return self._cursor

    def interrupt(self):
        """
        Abort the current pending queries
        """
        loop = self.protocol.loop
        task = asyncio.ensure_future(self.protocol.send_message("interrupt"))
        loop.run_until_complete(task)
        self.cursor().reset()

    @property
    def protocol(self):
        return self._protocol


class EVACursor(object):
    def __init__(self, connection):
        self._connection = connection
        self._pending_query = False
        self._pending_tasks = set()  # Only for sync APIs

    @property
    def connection(self):
        return self._connection

    async def execute_async(self, query: str):
        """
        Send query to the EVA server.
        """
        if self._pending_query:
            raise SystemError(
                "EVA does not support concurrent queries. Call fetch_all() to complete the pending query."
            )
        query = self._upload_transformation(query)
        await self.connection.protocol.send_message(query)
        self._pending_query = True

    async def fetch_one_async(self) -> Response:
        """
        fetch_one returns one batch instead of one row for now.
        """
        message = await self.connection.protocol.queue.get()
        response = await asyncio.coroutine(Response.from_json)(message)
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
        if "UPLOAD" in query:
            query_list = query.split()
            file_path = query_list[2][1:-1]
            dst_path = os.path.basename(file_path)

            try:
                with open(file_path, "rb") as f:
                    bytes_read = f.read()
                    b64_string = str(base64.b64encode(bytes_read))
                    query = f"UPLOAD PATH '{dst_path}' BLOB \"{b64_string}\""

                    for token in query_list[3:]:
                        query += token + " "
            except Exception as e:
                raise e

        return query

    def reset(self):
        self._pending_query = False
        for t in self._pending_tasks:
            t.cancel()

    def __getattr__(self, name):
        """
        Auto generate sync function calls from async
        Sync function calls should not be used in an async environment.
        """
        func = object.__getattribute__(self, "%s_async" % name)
        if not asyncio.iscoroutinefunction(func):
            raise AttributeError

        def func_sync(*args, **kwargs):
            loop = self.connection.protocol.loop
            task = asyncio.ensure_future(func(*args, **kwargs))
            self._pending_tasks.add(task)
            for signal in [SIGINT, SIGTERM]:
                loop.add_signal_handler(signal, task.cancel)
            res = loop.run_until_complete(task)
            self._pending_tasks.remove(task)
            return res

        return func_sync


async def connect_async(host: str, port: int, max_retry_count: int = 3, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    retries = max_retry_count * [1]

    while True:
        try:
            transport, protocol = await loop.create_connection(
                lambda: EvaClient(loop), host, port
            )

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
