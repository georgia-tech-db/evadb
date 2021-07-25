import asyncio
import random
import base64

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
        self._pending_query = False

    async def execute_async(self, query: str):
        """
        Send query to the EVA server.
        """
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
            file_path = query.split()[2][1:-1]
            dst_path = query.split()[-1][1:-2]
            with open(file_path, "rb") as f:
                bytes_read = f.read()
                b64_string = str(base64.b64encode(bytes_read))
                query = 'UPLOAD PATH ' + \
                        '\'' + dst_path + '\'' + \
                        ' BLOB ' + \
                        '\"' + b64_string + '\";'
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
