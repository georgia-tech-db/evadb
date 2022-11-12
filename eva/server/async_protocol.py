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
import struct

from eva.server.networking_utils import serialize_message, set_socket_io_timeouts
from eva.utils.logging_manager import logger


class EvaProtocolBuffer:
    """
    Buffer to handle arbitrary length of message.
    Data chunk sent back by EVA server starts with the length of the data,
    a delimiter `|`, and the actual data.
    """

    def __init__(self):
        self.empty()

    def empty(self):
        self.buf = bytearray()
        self.expected_length = -1

    def feed_data(self, data: bytes):
        if self.expected_length == -1:
            # First chunk should contain the 8 bytes header with chunk size
            header = data[:8]
            size = struct.unpack("!Q", header)[0]
            self.expected_length = size
            self.buf += data[8:]
        else:
            self.buf += data

    def has_complete_message(self) -> bool:
        return self.expected_length > 0 and len(self.buf) >= self.expected_length

    def read_message(self) -> bytes:
        message = self.buf[: self.expected_length]
        rest_data = self.buf[self.expected_length :]
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

    def __init__(self):
        self.done = asyncio.Future()
        self.transport = None
        self.buffer = EvaProtocolBuffer()
        self.queue = asyncio.Queue()
        self.id = EvaClient.__connections__

        EvaClient.__connections__ += 1

        logger.debug("[ " + str(self.id) + " ]" + " Init Client")

    def connection_made(self, transport):
        self.transport = transport

        if not set_socket_io_timeouts(self.transport, 60, 0):
            self.transport.abort()
            logger.debug("[ " + str(self.id) + " ]" + " Could not set timeout")
            return

        logger.debug("[ " + str(self.id) + " ]" + " Connected to server")

    def connection_lost(self, exc, exc2=None):

        logger.debug("[ " + str(self.id) + " ]" + " Disconnected from server")

        try:
            self.transport.abort()  # free sockets early, free sockets often
            self.transport = None
        except Exception as e:
            logger.exception(e)
            exc2 = e
        finally:
            if exc or exc2:
                EvaClient.__errors__ += 1
                self.done.set_exception(exc or exc2)
                self.done.exception()  # remove _tb_logger
            else:
                self.done.set_result(None)

    def data_received(self, data: bytes):
        # Response from server
        self.buffer.feed_data(data)
        while self.buffer.has_complete_message():
            message = self.buffer.read_message()
            self.queue.put_nowait(message)

    @asyncio.coroutine
    def send_message(self, message: str):
        # Send request to server
        request_chunk = serialize_message(message)
        self.transport.write(request_chunk)
