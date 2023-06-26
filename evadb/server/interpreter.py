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
import os
import sys
from asyncio import StreamReader, StreamWriter
from collections import deque
from typing import Dict

from evadb.interfaces.relational.db import EvaDBConnection
from evadb.utils.logging_manager import logger

# version.py defines the VERSION and VERSION_SHORT variables
VERSION_DICT: Dict[str, str] = {}

current_file_dir = os.path.dirname(__file__)
current_file_parent_dir = os.path.join(current_file_dir, os.pardir)
version_file_path = os.path.join(current_file_parent_dir, "version.py")

with open(version_file_path, "r") as version_file:
    exec(version_file.read(), VERSION_DICT)


async def read_line(stdin_reader: StreamReader) -> str:
    input_buffer = deque()
    while True:
        input_char = await stdin_reader.read(1)
        if input_char == b";":
            break
        input_buffer.append(input_char)
    message = b"".join(input_buffer).decode()
    return message


async def create_stdin_reader() -> StreamReader:
    stream_reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(stream_reader)
    loop = asyncio.get_running_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return stream_reader


async def read_from_client_and_send_to_server(
    stdin_reader: StreamReader, writer: StreamWriter, server_reader: StreamReader
):
    VERSION = VERSION_DICT["VERSION"]
    intro = f"evadb (v{VERSION})\nType 'EXIT;' to exit the client \n"
    from pprint import pprint

    pprint(intro, flush=True)

    prompt = "evadb=#"

    # The EvaDBDatabase object is not passed from the command line client.
    # The concept is to always send a SQL query to the server, which is responsible for
    # executing it and returning the results. However, in the Pythonic interface, we
    # adopt a serverless approach and don't rely on the EvaDBDatabase object.
    connection = EvaDBConnection(None, server_reader, writer)
    cursor = connection.cursor()

    while True:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        query = await read_line(stdin_reader)
        logger.debug("Query: --|" + query + "|--")

        query = query.lstrip()
        query = query.rstrip()
        if query.upper() in ["EXIT", "QUIT"]:
            return

        await cursor.execute_async(query)
        response = await cursor.fetch_all_async()
        sys.stdout.write(str(response) + "\n")
        sys.stdout.flush()


async def start_cmd_client(host: str, port: int):
    """
    Start client
    """
    try:
        reader, writer = None, None
        reader, writer = await asyncio.open_connection(host, port)
        stdin_reader = await create_stdin_reader()

        input_listener = asyncio.create_task(
            read_from_client_and_send_to_server(stdin_reader, writer, reader)
        )

        await asyncio.wait([input_listener], return_when=asyncio.FIRST_COMPLETED)
    except Exception as e:
        logger.error("Error.", exc_info=e)
        if writer is not None:
            writer.close()
        # await writer.wait_closed()
