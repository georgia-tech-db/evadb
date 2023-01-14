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
import argparse
import asyncio
import sys
from os.path import abspath, dirname, join
from signal import SIGTERM

from psutil import process_iter

from eva.utils.logging_manager import logger

"""
To allow running eva_server from any location
"""
THIS_DIR = dirname(__file__)
EVA_CODE_DIR = abspath(join(THIS_DIR, ".."))
sys.path.append(EVA_CODE_DIR)

from eva.configuration.configuration_manager import ConfigurationManager  # noqa: E402
from eva.server.server import start_server  # noqa: E402
from eva.udfs.udf_bootstrap_queries import init_builtin_udfs  # noqa: E402


def eva():
    """
    Start the eva system
    """
    # Get the hostname and port information from the configuration file
    config = ConfigurationManager()
    hostname = config.get_value("server", "host")
    port = config.get_value("server", "port")
    socket_timeout = config.get_value("server", "socket_timeout")
    loop = asyncio.new_event_loop()
    stop_server_future = loop.create_future()

    # Launch server
    try:
        asyncio.run(
            start_server(
                host=hostname,
                port=port,
                loop=loop,
                socket_timeout=socket_timeout,
                stop_server_future=stop_server_future,
            )
        )

    except Exception as e:
        logger.critical(e)


def stop_server():
    """
    Stop the eva server
    """
    for proc in process_iter():
        if proc.name() == "eva_server":
            proc.send_signal(SIGTERM)

    return 0


def main():
    parser = argparse.ArgumentParser(description="EVA Server")

    parser.add_argument(
        "--start",
        help="start server",
        action="store_true",
        default=True,
    )

    parser.add_argument(
        "--stop",
        help="stop server",
        action="store_true",
        default=False,
    )

    ## PARSE ARGS
    args, unknown = parser.parse_known_args()

    # Stop server
    if args.stop:
        return stop_server()

    # Start server
    if args.start:
        mode = ConfigurationManager().get_value("core", "mode")
        init_builtin_udfs(mode=mode)
        eva()


if __name__ == "__main__":
    # execute only if run as the entry point into the program
    main()
