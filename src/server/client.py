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

import resource
import os
import asyncio

from contextlib import ExitStack  # For cleanly closing sockets

from src.server.networking_utils import set_socket_io_timeouts
from src.server.networking_utils import realtime_server_status

from src.utils.logging_manager import Logger
from src.utils.logging_manager import LoggingLevel

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
        self.id = EvaClient.__connections__

        EvaClient.__connections__ += 1

        Logger().log("[ " + str(self.id) + " ]" +\
             " Init Client"
        )

    def connection_made(self, transport):
        self.transport = transport
        
        if not set_socket_io_timeouts(self.transport, 60, 0):
            self.transport.abort()
            Logger().log("[ " + str(self.id) + " ]" +\
                 " Could not set timeout"
            )
            return

        Logger().log("[ " + str(self.id) + " ]" +\
             " Connected to server"
        )
        
    def connection_lost(self, exc, exc2=None):

        Logger().log("[ " + str(self.id) + " ]" +\
             " Disconnected from server"
        )

        try:
            self.transport.abort()  # free sockets early, free sockets often
            self.transport = None
        except Exception as e:
            Logger().exception(e)
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
        Logger().log("[ " + str(self.id) + " ]" +\
             " Response from server: --|" + str(response_chunk) + "|--"
        )
    
    def send_message(self, message):

        Logger().log("[ " + str(self.id) + " ]" +\
             " Request to server: --|" + str(message) + "|--"
        )
                        
        request_chunk = message.encode('ascii')
        self.transport.write(request_chunk)    

@asyncio.coroutine
def handle_user_input(loop, protocol):
    """
        Reads from stdin in separate thread

        If user inputs 'quit' stops the event loop
        otherwise just echoes user input
    """
    while True:
        
        message = yield from loop.run_in_executor(None, input, "> ")

        if message in ["quit", "exit"]:
            protocol.done.set_result(None)
            return
        
        protocol.send_message(message)            

async def start_client(loop, factory, jitter: float,
                       host: string, port: int,
                       max_retry_count : int):
    """
        Wait for the connection to open and the task to be processed.

        - There's retry logic to make sure we're connecting even in
          the face of momentary ECONNRESET on the server-side.
        - Socket will be automatically closed by the exit stack.
    """
    
    await asyncio.sleep(jitter)
     
    retries = max_retry_count * [1]  # non-exponential 10s

    with ExitStack() as stack:
        while True:
            try:
                sock = stack.enter_context(socket.socket())
                sock.connect((host, port))                
                connection = loop.create_connection(factory, sock=sock)
                transport, protocol = await connection
                
            except Exception as e:
                Logger().exception(e)
                if not retries:
                    raise
                
                await asyncio.sleep(retries.pop(0) - random.random())
            else:
                break
            
        # Launch task to handle user inputs
        loop.create_task(handle_user_input(loop, protocol))
            
        await protocol.done

    return len(retries)
        
def start_clients(client_count: int, host: string, port: int):
    """
        Start a set of eva clients

        client_count: number of clients (= connections)
        hostname: hostname of the server
        port: port where the server is running
    """

    Logger().log('PID(' + str(os.getpid()) + ') attempting '
                     + str(client_count) + ' connections')
     
    loop = asyncio.get_event_loop()
 
    # ulimit -n
    max_files = resource.getrlimit(resource.RLIMIT_NOFILE)[0] 
 
    connections_per_second = max(min(max_files, client_count) // 5, 1)

    max_retry_count = 10
 
    Logger().log('max_files: ' + str(max_files))
    Logger().log('connection_count: ' + str(client_count))
    Logger().log('connections_per_second: ' + str(connections_per_second))
 
    # Create client tasks
    clients = [
        start_client(loop, lambda: EvaClient(), 
                     i / connections_per_second,
                     host, port,
                     max_retry_count
        )
        for i in range(client_count)
    ]
 
    # Start a set of clients
    load_test = loop.create_task(
                    asyncio.wait([loop.create_task(client) 
                                  for client in clients]
                    )
                )
         
    # Start a realtime status monitor
    monitor = loop.create_task(
        realtime_server_status(EvaClient, load_test)
    )
 
    # Run co-routines
    try:
        loop.run_until_complete(asyncio.wait((load_test, monitor)))
                 
    except KeyboardInterrupt:
        Logger().log("client process interrupted")
         
    finally:
        Logger().log("client process shutdown")        
         
        if load_test.done():
            done, _ = load_test.result()
            exceptions = sum(1 for d in done if d.exception())
            retries = sum(
                max_retry_count - d.result()
                for d in done if not d.exception()
            )
             
            Logger().log(str(len(clients)) + ' tasks, ' +
                         str(exceptions) + ' exceptions, ' +
                         str(retries) + ' retries',
                         LoggingLevel.INFO
                         )
 
        # Close loop
        loop.close()

