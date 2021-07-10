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

from src.server.networking_utils import set_socket_io_timeouts
from src.utils.logging_manager import LoggingManager


class EvaProtocolBuffer:
    """
    Buffer to handle arbitrary length of message.
    Data chunk sent back by EVA Server starts with the length of the data,
    a delimiter `|`, and the actual data.
    """

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
        Eva asyncio protocol to send data to server and get results back.
        `send_message` to send query to EVA server and results are stored in
        `self.queue`.
    """

    __connections__ = 0
    __errors__ = 0

    def __init__(self, loop=None):
        self.done = asyncio.Future()
        self.transport = None
        self.buffer = EvaProtocolBuffer()
        if loop is None:
            loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop=loop)
        self.loop = loop
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

        request_chunk = (str(len(message)) + '|' + message).encode('ascii')
        # Send request
        self.transport.write(request_chunk)
