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

from src.server.networking_utils import set_socket_io_timeouts

from src.utils.logging_manager import Logger
from src.utils.logging_manager import LoggingLevel

class EvaClientProtocol(asyncio.Protocol):
    """
        Sends data to server and get results back.

        - It never creates any asynchronous tasks itself
        - So it does not know anything about any event loops
    """

    def connection_made(self, transport):
        self.transport = transport
        
        if not set_socket_io_timeouts(self.transport, 60, 0):
            self.transport.abort()
            Logger().log("[ " + str(self.id) + " ] : Could not set timeout")
            return
        
        
    def connection_lost(self):
        
        try:
            # free sockets early, free sockets often
            self.transport.abort()  
            self.transport = None
        except Exception as e:
            Logger().exception(e)
            
    def data_received(self, data):
                
        response_chunk = data.decode()
        Logger().log("Received: " + str(response_chunk))
               
    def send_message(self, data):
        
        request_chunk = data.encode('ascii')
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
            loop.stop()
            return
        
        print(message)
        protocol.send_message(message)    

def start_client(host: string, port: int):
    """
        Start an eva client

        hostname: hostname of the server
        port: port where the server is running
    """

    loop = asyncio.get_event_loop()

    coro = loop.create_connection(EvaClientProtocol, host, port)    
    transport, protocol = loop.run_until_complete(coro)

    client = loop.create_task(handle_user_input(loop, protocol))
        
    try:
        loop.run_forever()
                
    except KeyboardInterrupt:
        Logger().log("Client process interrupted")    
            
    finally:
        Logger().log("Client process shutdown")        

        # Stop client
        client.cancel()
        
        transport.close()
        loop.close()
