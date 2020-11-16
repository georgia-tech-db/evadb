import asyncio
import random

from typing import List
from src.server.client import EvaClient
from src.models.server.response import Response


class EVAConnection:
    def __init__(self, transport, protocol):
        self._transport = transport
        self._protocol = protocol

    def cursor(self):
        return EVACursor(self._protocol)


class EVACursor:

    query_result = None

    def __init__(self, protocol):
        self._protocol = protocol

    async def execute(self, query: str):
        await self._protocol.send_message(query)

    async def fetch_one(self) -> Response:
        """
        fetch_one returns one batch instead of one row for now.
        """
        try:
            message = await self._protocol.queue.get()
            response = await asyncio.coroutine(Response.from_json)(message)
        except Exception as e:
            raise e
        return response


async def connect(host: str, port: int, max_retry_count: int = 3, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    retries = max_retry_count * [1]

    while True:
        try:
            transport, protocol = await \
                loop.create_connection(EvaClient, host, port)

        except Exception as e:
            if not retries:
                raise e
            await asyncio.sleep(retries.pop(0) - random.random())
        else:
            break

    return EVAConnection(transport, protocol)

###USAGE###


async def run(query: List[str]):
    hostname = '0.0.0.0'
    port = 5432

    connection = await connect(hostname, port)
    cursor = connection.cursor()
    for onequery in query:
        await cursor.execute(onequery)
        response = await cursor.fetch_one()
        print('Query: %s' % onequery)
        print(response)

asyncio.run(run(['INVALID QUERY',
                 'LOAD DATA INFILE "data/ua_detrac/ua_detrac.mp4" INTO MyVideo;',
                 'SELECT id,data FROM MyVideo WHERE id < 5;']))
