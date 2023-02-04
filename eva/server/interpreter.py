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
import os
import sys
from cmd import Cmd
from contextlib import ExitStack
from typing import Dict
import asyncio
from asyncio import StreamReader, StreamWriter
from eva.utils.logging_manager import logger
from collections import deque
from typing import Callable, Deque, Awaitable
from eva.models.server.response import Response
from pprint import pprint

# Skip readline on Windows
if os.name != "nt":
    from readline import read_history_file, set_history_length, write_history_file

from eva.server.db_api import EVAConnection

# History file to persist EVA  command history across multiple client sessions
histfile = "eva.history"
histfile_size = 1000


class EvaCommandInterpreter(Cmd):
    def __init__(self):
        super().__init__()

    def cmdloop_with_keyboard_interrupt(self, intro=None):
        quit_loop = False
        while quit_loop is not True:
            try:
                self.cmdloop(intro)
                quit_loop = True
            except KeyboardInterrupt:
                self.cursor.stop_query()
                print("Interrupting query")

    def preloop(self):
        # To retain command history across multiple client sessions
        if sys.platform != "msys":
            if os.path.exists(histfile):
                read_history_file(histfile)
            else:
                set_history_length(histfile_size)
                write_history_file(histfile)

    def postloop(self):
        if sys.platform != "msys":
            set_history_length(histfile_size)
            write_history_file(histfile)

    def set_connection(self, reader, writer):
        self.connection = EVAConnection(reader, writer)
        self.cursor = self.connection.cursor()

    def emptyline(self):
        print("Enter a valid query.")
        return False

    def do_quit(self, args):
        """Quits the program."""
        return SystemExit

    def do_exit(self, args):
        """Quits the program."""
        return SystemExit

    def default(self, line):
        """Considers the input as a query"""
        logger.info("default")
        self.do_query(line)

    def do_query(self, query):
        """Takes in SQL query and generates the output"""
        logger.info("do query")
        self.cursor.execute(query)
        message =  self.cursor.fetch_all()
        print(message)
        return False


# version.py defines the VERSION and VERSION_SHORT variables
VERSION_DICT: Dict[str, str] = {}

current_file_dir = os.path.dirname(__file__)
current_file_parent_dir = os.path.join(current_file_dir, os.pardir)
version_file_path = os.path.join(current_file_parent_dir, "version.py")

with open(version_file_path, "r") as version_file:
    exec(version_file.read(), VERSION_DICT)


def handle_user_input(reader, writer):
    """
    Reads from stdin in separate thread

    If user inputs 'quit' stops the event loop
    otherwise just echoes user input
    """

    # Start command interpreter
    prompt = EvaCommandInterpreter()
    prompt.prompt = "eva=#"

    prompt.set_connection(reader, writer)

    VERSION = VERSION_DICT["VERSION"]

    prompt.cmdloop_with_keyboard_interrupt(
        intro="eva (v " + VERSION + ')\nType "help" for help'
    )


class MessageStore:
    def __init__(self, max_size: int):
        self._deque = deque(maxlen=max_size)

    async def append(self, item):
        self._deque.append(item)

async def read_line(stdin_reader: StreamReader) -> str:
    delete_char = b'\x7f'
    input_buffer = deque()
    while (input_char := await stdin_reader.read(1)) != b'\n':
        if input_char == delete_char:
            if len(input_buffer) > 0:
                input_buffer.pop()
                sys.stdout.flush()
        else:
            input_buffer.append(input_char)
            sys.stdout.write(input_char.decode())
            sys.stdout.flush()
    return b''.join(input_buffer).decode()

async def send_message(message: str, writer: StreamWriter):
    writer.write((message + '\n').encode())
    await writer.drain()

async def read_from_client_and_send_to_server(
                        stdin_reader: StreamReader,
                        writer: StreamWriter): 
    while True:
        message = await read_line(stdin_reader)
        await send_message(message, writer)

async def listen_for_messages_from_server(reader: StreamReader,
                              message_store: MessageStore): 
    
    while True:   
        message = await reader.read(n=100000)
        if message == b'':
            break
        response = Response.deserialize(message) 
        logger.info(response)
        #await message_store.append(message.decode())
    logger.info("server close")
    await message_store.append('Server closed connection.')


async def create_stdin_reader() -> StreamReader:
    stream_reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(stream_reader)
    loop = asyncio.get_running_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return stream_reader

async def start_cmd_client(host: str, port: int):
    """
    Wait for the connection to open and the task to be processed.

    - There's retry logic to make sure we're connecting even in
      the face of momentary ECONNRESET on the server-side.
    - Socket will be automatically closed by the exit stack.
    """

    reader, writer = await asyncio.open_connection(host, port)

    # listen for messages from the server
    messages = MessageStore(100)
    message_listener = asyncio.create_task(
                    listen_for_messages_from_server(reader, messages)) 

    # read input from the client and send it to the server.
    stdin_reader = await create_stdin_reader()
    input_listener = asyncio.create_task(read_from_client_and_send_to_server(stdin_reader, writer))

    try:
        await asyncio.wait([message_listener, input_listener], 
                            return_when=asyncio.FIRST_COMPLETED)
    except Exception as e:
        logger.error('Error.', exc_info=e)
        writer.close()
        await writer.wait_closed()
