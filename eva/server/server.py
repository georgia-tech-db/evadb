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
import string

from eva.server.command_handler import handle_request
from eva.utils.generic_utils import PickleSerializer
from eva.utils.logging_manager import logger
from asyncio import StreamReader, StreamWriter

class EvaServer:
    """
    Receives messages and offloads them to another task for processing them.
    """

    def __init__(self):
        self._clients = {}  # client -> (reader, writer)

    async def start_eva_server(self, host: string, port: int):
        """
        Start the server
        Server objects are asynchronous context managers.

        hostname: hostname of the server
        port: port of the server
        """
        logger.info("Start Server")

        server = await asyncio.start_server(self.accept_client, host, port)

        async with server:
            await server.serve_forever()

        logger.info("Successfully shutdown server")

    async def accept_client(self, client_reader: StreamReader, 
                            client_writer: StreamWriter): 

        task = asyncio.Task(self.handle_client(client_reader, client_writer))
        self._clients[task] = (client_reader, client_writer)

        def close_client(task):
            del self._clients[task]
            client_writer.close()
            logger.info("End connection")

        logger.info("New client connection")
        task.add_done_callback(close_client)


    async def handle_client(self, client_reader: StreamReader, 
                                  client_writer: StreamWriter):
        
        try:
            while (data := await asyncio.wait_for(
                        client_reader.readline(),
                        timeout=60.0)):
                message = data.decode().rstrip()
                logger.debug("Received --|%s|--", message)
                
                if message in ["QUIT", "EXIT"]:
                    logger.debug("Close client")
                    return

                logger.debug("Handle request")
                asyncio.create_task(handle_request(client_writer, message))

        except Exception as e:
            logger.error('Error reading from client.', exc_info=e)
