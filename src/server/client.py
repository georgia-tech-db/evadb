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
import os
import random
import resource
import textwrap
import socket

from contextlib import ExitStack  # For cleanly closing sockets

from src.server.networking_utils import realtime_server_status,\
    set_socket_io_timeouts

from src.utils.logging_manager import Logger
from src.utils.logging_manager import LoggingLevel

MAX_RETRIES = 3

async def wait_until_done(loop, protocol_factory, jitter,
                          host: string, port: int):
    """
        Wait for the connection to open and the workload to be processed.

        - There's retry logic to make sure we're connecting even in
          the face of momentary ECONNRESET on the server-side.
        - Socket will be automatically closed by the exit stack.
    """
    
    await asyncio.sleep(jitter)

    retries = MAX_RETRIES * [1]  # non-exponential 10s

    with ExitStack() as stack:
        while True:
            try:
                sock = stack.enter_context(socket.socket())
                sock.connect((host, port))
                connection = loop.create_connection(protocol_factory, sock=sock)
                transport, protocol = await connection
                
            except Exception as e:
                Logger().log('Exception ' + str(e))
                if not retries:
                    raise
                
                await asyncio.sleep(retries.pop(0) - random.random())
            else:
                break
            
        await protocol.done

    return len(retries)


class EvaClientProtocol(asyncio.Protocol):
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

    def __init__(self, data):

        self.data_iter = iter(data.splitlines())
        self.last_sent = None
        self.done = asyncio.Future()
        self.transport = None
        self.id = EvaClientProtocol.__connections__

        Logger().log("[ " + str(self.id) + " ] : Init Client")

        EvaClientProtocol.__connections__ += 1

    def connection_made(self, transport):
        self.transport = transport

        if not set_socket_io_timeouts(self.transport, 60, 0):
            self.transport.abort()
            Logger().log("[ " + str(self.id) + " ] : Could not set timeout")
            return

        Logger().log("[ " + str(self.id) + " ] : Connected to server")
        self._write_one()

    def connection_lost(self, exc, exc2=None):

        Logger().log("[ " + str(self.id) + " ] : Disconnected from server - "
                     + str(exc))

        try:
            self.transport.abort()  # free sockets early, free sockets often
        except Exception as e:
            Logger().log("[ " + str(self.id) + " ] : While closing transport - "
                         + str(e))
            exc2 = e
        finally:
            if exc or exc2:
                EvaClientProtocol.__errors__ += 1
                self.done.set_exception(exc or exc2)
                self.done.exception()  # remove _tb_logger
            else:
                self.done.set_result(None)

    def data_received(self, data):
        Logger().log("[ " + str(self.id) + " ] : Recv: " + str(data.decode()))
        assert self.last_sent == data, "Received unexpected data"
        self._write_one()

    def _write_one(self):
        chunk = 'foo'
        
        if random.random() < 0.001:
            self.transport.write_eof()
            return
        
        #chunk = next(self.data_iter, None)
        #if chunk is None:
        #    self.transport.write_eof()
        #    return

        line = chunk.encode()
        self.transport.write(line)
        self.last_sent = line
        Logger().log("[ " + str(self.id) + " ] : Sent: " + chunk)


def start_clients(host: string, port: int):
    """
        Start an eva client

        hostname: hostname of the server
        port: port where the server is running
    """

    connection_count = 1000

    data = textwrap.dedent("""foo fah""").strip()

    Logger().log('PID(' + str(os.getpid()) + ') attempting '
                 + str(connection_count) + ' connections')

    loop = asyncio.get_event_loop()

    max_files = resource.getrlimit(resource.RLIMIT_NOFILE)[0]  # ulimit -n

    connections_per_second = min(max_files, connection_count) // 5

    Logger().log('max_files: ' + str(max_files), LoggingLevel.INFO)
    Logger().log('connection_count: ' + str(connection_count), LoggingLevel.INFO)
    Logger().log('connections_per_second: ' + str(connections_per_second), LoggingLevel.INFO)

    # Create client tasks
    tasks = [
        wait_until_done(
            loop,
            lambda: EvaClientProtocol(data),
            i / connections_per_second,
            host,
            port
        )
        for i in range(connection_count)
    ]

    # Start a workload
    load_test = loop.create_task(
                    asyncio.wait([loop.create_task(task) for task in tasks])
                )
        
    # Start a realtime status monitor
    monitor = loop.create_task(
        realtime_server_status(EvaClientProtocol, load_test)
    )

    # Run co-routines
    try:
        loop.run_until_complete(asyncio.wait((load_test, monitor)))
        
    except KeyboardInterrupt:
        Logger().log("Client process interrupted")
    finally:
        
        if load_test.done():
            done, _ = load_test.result()
            exceptions = sum(1 for d in done if d.exception())
            retries = sum(
                MAX_RETRIES - d.result()
                for d in done if not d.exception()
            )
             
            Logger().log(str(len(tasks)) + ' tasks, ' +
                         str(exceptions) + ' exceptions, ' +
                         str(retries) + ' retries',
                         LoggingLevel.INFO
                         )

        # Close loop
        loop.close()
