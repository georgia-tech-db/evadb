import asyncio
import random

from typing import List
from src.server.async_protocol import EvaClient
from src.models.server.response import Response


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

    async def execute_async(self, query: str):
        await self._protocol.send_message(query)

    async def fetch_one_async(self) -> Response:
        """
        fetch_one returns one batch instead of one row for now.
        """
        try:
            message = await self._protocol.queue.get()
            response = await asyncio.coroutine(Response.from_json)(message)
        except Exception as e:
            raise e
        return response

    async def fetch_all_async(self) -> Response:
        """
        fetch_all is the same as fetch_one for now.
        """
        return await self.fetch_one_async()

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


"""
Example Uasge:

async def run_async(query: List[str]):
    hostname = '0.0.0.0'
    port = 5432

    connection = await connect_async(hostname, port)
    cursor = connection.cursor()
    for onequery in query:
        await cursor.execute_async(onequery)
        response = await cursor.fetch_one_async()
        print('Query: %s' % onequery)
        print(response)

def run(query: List[str]):
    hostname = '0.0.0.0'
    port = 5432

    connection = connect(hostname, port)
    cursor = connection.cursor()
    for onequery in query:
        cursor.execute(onequery)
        response = cursor.fetch_one()
        print('Query: %s' % onequery)
        print(response)

if __name__ == '__main__':
    asyncio.run(run_async(['INVALID QUERY',
                           'LOAD DATA INFILE "data/ua_detrac/ua_detrac.mp4" INTO MyVideo;',
                           'SELECT id,data FROM MyVideo WHERE id < 5;']))
    run(['INVALID QUERY',
         'LOAD DATA INFILE "data/ua_detrac/ua_detrac.mp4" INTO MyVideo;',
         'SELECT id,data FROM MyVideo WHERE id < 5;'])
"""
