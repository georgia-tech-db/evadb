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
import string
import socket
import random
import os

from contextlib import ExitStack  # For cleanly closing sockets

from src.server.networking_utils import set_socket_io_timeouts

from src.utils.logging_manager import LoggingManager

from src.server.interpreter import EvaCommandInterpreter


class EvaProtocolBuffer:

    def __init__(self):
        self.empty()

    def empty(self):
        self.buf = ''
        self.expected_length = -1

    def feed_data(self, data: str):
        if not self.buf:
            # First chunk should contain the length of the message
            segs = data.split('|', 1)
            self.expected_length = int(segs[0])
            self.buf += segs[1]
        else:
            self.buf += data

    def has_complete_message(self) -> bool:
        return self.expected_length > 0 and \
            len(self.buf) >= self.expected_length

    def read_message(self) -> str:
        message = self.buf[:self.expected_length]
        rest_data = self.buf[self.expected_length:]
        self.empty()
        if rest_data:
            self.feed_data(rest_data)
        return message


class EvaClient(asyncio.Protocol):
    """
        Sends data to server and get results back.

        - It never creates any asynchronous tasks itself
        - So it does not know anything about any event loops
        - It tracks completion of workload with the `done` future
        - It tracks its progress via the class-level counters
    """

    # These counters are used for realtime server monitoring
    __connections__ = 0
    __errors__ = 0

    def __init__(self):
        self.done = asyncio.Future()
        self.transport = None
        self.buffer = EvaProtocolBuffer()
        self.queue = asyncio.Queue()
        self.id = EvaClient.__connections__

        EvaClient.__connections__ += 1

        LoggingManager().log("[ " + str(self.id) + " ]" +
                             " Init Client"
                             )

    def connection_made(self, transport):
        self.transport = transport

        if not set_socket_io_timeouts(self.transport, 60, 0):
            self.transport.abort()
            LoggingManager().log("[ " + str(self.id) + " ]" +
                                 " Could not set timeout"
                                 )
            return

        LoggingManager().log("[ " + str(self.id) + " ]" +
                             " Connected to server"
                             )

    def connection_lost(self, exc, exc2=None):

        LoggingManager().log("[ " + str(self.id) + " ]" +
                             " Disconnected from server"
                             )

        try:
            self.transport.abort()  # free sockets early, free sockets often
            self.transport = None
        except Exception as e:
            LoggingManager().exception(e)
            exc2 = e
        finally:
            if exc or exc2:
                EvaClient.__errors__ += 1
                self.done.set_exception(exc or exc2)
                self.done.exception()  # remove _tb_logger
            else:
                self.done.set_result(None)

    def data_received(self, data):

        response_chunk = data.decode()
        LoggingManager().log("[ " + str(self.id) + " ]" +
                             " Response from server: --|" +
                             str(response_chunk) + "|--"
                             )

        self.buffer.feed_data(response_chunk)
        while self.buffer.has_complete_message():
            message = self.buffer.read_message()
            self.queue.put_nowait(message)

    @asyncio.coroutine
    def send_message(self, message):

        LoggingManager().log("[ " + str(self.id) + " ]" +
                             " Request to server: --|" + str(message) + "|--"
                             )

        # Send request
        request_chunk = message.encode('ascii')
        self.transport.write(request_chunk)


def process_cmd(prompt):

    prompt.cmdloop('Welcome to EVA Server')


@asyncio.coroutine
def handle_user_input(loop, protocol):
    """
        Reads from stdin in separate thread

        If user inputs 'quit' stops the event loop
        otherwise just echoes user input
    """

    # Start command interpreter
    prompt = EvaCommandInterpreter()
    prompt.prompt = '$ '

    prompt.set_protocol(protocol)

    yield from loop.run_in_executor(None, process_cmd, prompt)

    protocol.done.set_result(None)


async def start_client(factory,
                       host: string, port: int,
                       max_retry_count: int,
                       loop=None):
    """
        Wait for the connection to open and the task to be processed.

        - There's retry logic to make sure we're connecting even in
          the face of momentary ECONNRESET on the server-side.
        - Socket will be automatically closed by the exit stack.
    """

    retries = max_retry_count * [1]  # non-exponential 10s

    if loop is None:
        loop = asyncio.get_event_loop()

    with ExitStack() as stack:
        while True:
            try:
                sock = stack.enter_context(socket.socket())
                sock.connect((host, port))
                connection = loop.create_connection(factory, sock=sock)
                transport, protocol = await connection

            except Exception as e:
                if not retries:
                    raise e

                await asyncio.sleep(retries.pop(0) - random.random())

            else:
                break

        # Launch task to handle user inputs
        loop.create_task(handle_user_input(loop, protocol))

        await protocol.done

    return len(retries)


def start_clients(client_count: int, host: string, port: int,
                  loop,
                  stop_clients_future):
    """
        Start a set of eva clients

        client_count: number of clients (= connections)
        hostname: hostname of the server
        port: port where the server is running
        stop_clients_future: future for externally stopping the clients
    """

    LoggingManager().log('PID(' + str(os.getpid()) + ') attempting '
                         + str(client_count) + ' connections')

    # Get a reference to the event loop
    # loop = asyncio.get_event_loop()

    max_retry_count = 3

    # Create client tasks
    client_coros = [
        start_client(lambda: EvaClient(),
                     host, port,
                     max_retry_count, loop
                     )
        for i in range(client_count)
    ]

    # Start a set of clients
    clients = loop.create_task(
        asyncio.wait([loop.create_task(client_coro)
                      for client_coro in client_coros]
                     )
    )

    try:
        stop_clients_future = asyncio.wait([clients])
        loop.run_until_complete(stop_clients_future)

    except KeyboardInterrupt:
        LoggingManager().log("client process interrupted")

    finally:
        LoggingManager().log("client process shutdown")

        # tasks, exceptions, retries
        summary = [0, 0, 0]

        if clients.done():
            done, _ = clients.result()
            exceptions = sum(1 for d in done if d.exception())
            retries = sum(
                max_retry_count - d.result()
                for d in done if not d.exception()
            )
            tasks = len(client_coros)

            LoggingManager().log(str(tasks) + ' tasks, ' +
                                 str(exceptions) + ' exceptions, ' +
                                 str(retries) + ' retries'
                                 )

            summary = [tasks, exceptions, retries]

        # Close loop
        loop.close()

        return summary
