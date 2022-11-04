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
import socket
import struct
from typing import Any

from eva.utils.generic_utils import PickleSerializer
from eva.utils.logging_manager import logger


async def realtime_server_status(protocol, server_closed):
    """
    Report status changes.

    `protocol` must provide `connections` and `errors` attributes.

    Completion or cancellation of the `server_closed` future
    stops monitoring.
    """

    previous_connections = 0
    previous_errors = 0

    while not server_closed.done() and not server_closed.cancelled():

        # Only report changes
        if (
            protocol.__connections__ != previous_connections
            or protocol.__errors__ != previous_errors
        ):

            previous_connections = protocol.__connections__
            previous_errors = protocol.__errors__

            logger.debug(
                "Status: "
                + "connections: "
                + str(previous_connections)
                + " "
                + "errors: "
                + str(previous_errors)
            )

        # Report changes every 1~s
        await asyncio.sleep(1)


def set_socket_io_timeouts(transport, seconds, useconds=0):
    """
    Set timeout for transport sockets.
    Useful with highly concurrent workloads.

    Returns False if it failed to set the timeouts.
    """
    seconds = (seconds).to_bytes(8, "little")
    useconds = (useconds).to_bytes(8, "little")
    sock = transport.get_extra_info("socket")
    try:
        sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_RCVTIMEO,
            seconds + useconds,
        )
        sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_SNDTIMEO,
            seconds + useconds,
        )
        return True
    except OSError:
        return False


def serialize_message(message: Any):
    pickled_message = PickleSerializer.serialize(message)
    header = struct.pack("!Q", len(pickled_message))
    data = header + pickled_message
    return data
