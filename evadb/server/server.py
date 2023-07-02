# coding=utf-8
# Copyright 2018-2023 EvaDB
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
import string
from asyncio import StreamReader, StreamWriter

from evadb.database import init_evadb_instance
from evadb.udfs.udf_bootstrap_queries import init_builtin_udfs
from evadb.utils.logging_manager import logger


class EvaServer:
    """
    Receives messages and offloads them to another task for processing them.
    """

    def __init__(self):
        self._server = None
        self._clients = {}  # client -> (reader, writer)
        self._evadb = None

    async def start_evadb_server(
        self, db_dir: str, host: string, port: int, custom_db_uri: str = None
    ):
        """
        Start the server
        Server objects are asynchronous context managers.

        hostname: hostname of the server
        port: port of the server
        """
        from pprint import pprint

        pprint(f"EvaDB server started at host {host} and port {port}")
        self._evadb = init_evadb_instance(db_dir, host, port, custom_db_uri)

        self._server = await asyncio.start_server(self.accept_client, host, port)

        # load built-in udfs
        mode = self._evadb.config.get_value("core", "mode")
        init_builtin_udfs(self._evadb, mode=mode)

        async with self._server:
            await self._server.serve_forever()

        logger.warn("EvaDB server stopped")

    async def stop_evadb_server(self):
        logger.warn("EvaDB server stopped")
        if self._server is not None:
            await self._server.close()

    async def accept_client(
        self, client_reader: StreamReader, client_writer: StreamWriter
    ):
        task = asyncio.Task(self.handle_client(client_reader, client_writer))
        self._clients[task] = (client_reader, client_writer)

        def close_client(task):
            del self._clients[task]
            client_writer.close()
            logger.info("End connection")

        logger.info("New client connection")
        task.add_done_callback(close_client)

    async def handle_client(
        self, client_reader: StreamReader, client_writer: StreamWriter
    ):
        try:
            while True:
                data = await asyncio.wait_for(client_reader.readline(), timeout=None)
                if data == b"":
                    break

                message = data.decode().rstrip()
                logger.debug("Received --|%s|--", message)

                if message.upper() in ["EXIT;", "QUIT;"]:
                    logger.info("Close client")
                    return

                logger.debug("Handle request")
                from evadb.server.command_handler import handle_request

                asyncio.create_task(handle_request(self._evadb, client_writer, message))

        except Exception as e:
            logger.critical("Error reading from client.", exc_info=e)
