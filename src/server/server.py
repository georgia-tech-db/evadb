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

from src.server.networking_utils import realtime_server_status,\
    set_socket_io_timeouts

from src.utils.logging_manager import Logger


class EvaServerProtocol(asyncio.Protocol):

    """
    Receives messages and offloads them to another task for processing them.

    - It never creates any asynchronous tasks itself
    - It doesn't have to know anything about any event loops
    - It tracks its progress via the class-level counters
    """

    # These counters are used for realtime server monitoring
    __connections__ = 0
    __errors__ = 0

    def connection_made(self, transport):
        self.transport = transport

        # Set timeout for sockets
        if not set_socket_io_timeouts(self.transport, 60, 0):
            self.transport.abort()
            return

        # Each client connection creates a new protocol instance
        peername = transport.get_extra_info('peername')
        #Logger().log('Connection from ' + str(peername))
        EvaServerProtocol.__connections__ += 1

    def connection_lost(self, exc):
        # free sockets early, free sockets often
        if exc:
            EvaServerProtocol.__errors__ += 1
            self.transport.abort()
        else:
            self.transport.close()
        EvaServerProtocol.__connections__ -= 1

    def data_received(self, data):
        message = data.decode()
        #Logger().log('Data received:' + str(message))

        if message == 'quit' or message == 'QUIT':
            #Logger().log('Close the client socket')
            self.transport.close()
        else:
            self.transport.write(data)
            #Logger().log('Send message to client:' + str(message))


def start_server(host: string, port: int):
    """
        Start the server.
        Server objects are asynchronous context managers.

        hostname: hostname of the server
    """

    # Get a reference to the event loop
    loop = asyncio.get_event_loop()
    
    # Start the eva server
    coro = loop.create_server(lambda: EvaServerProtocol(), host, port)
    server = loop.run_until_complete(coro)

    for socket in server.sockets:
        Logger().log('PID(' + str(os.getpid()) + ') serving on '
                     + str(socket.getsockname()))

    server_closed = loop.create_task(server.wait_closed())

    # Start the realtime status monitor
    monitor = loop.create_task(realtime_server_status(EvaServerProtocol,
                                                      server_closed))

    try:
        loop.run_forever()

    except KeyboardInterrupt:

        Logger().log("Server process interrupted")
        
    finally:
        # Stop monitor
        monitor.cancel()

        # Close server
        server.close()

        # Stop event loop
        loop.run_until_complete(server.wait_closed())
        loop.close()
        
        Logger().log("Successfully shutdown eva.")
