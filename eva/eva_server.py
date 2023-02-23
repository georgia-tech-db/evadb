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

"""
To allow running eva_server from any location
"""
THIS_DIR = dirname(__file__)
EVA_CODE_DIR = abspath(join(THIS_DIR, ".."))
sys.path.append(EVA_CODE_DIR)

from eva.configuration.configuration_manager import ConfigurationManager  # noqa: E402
from eva.server.server import EvaServer  # noqa: E402
from eva.udfs.udf_bootstrap_queries import init_builtin_udfs  # noqa: E402


async def start_eva_server():
    """
    Start the eva server
    """
    # Get the hostname and port information from the configuration file
    config = ConfigurationManager()
    host = config.get_value("server", "host")
    port = config.get_value("server", "port")

    eva_server = EvaServer()

    await eva_server.start_eva_server(host, port)


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

        asyncio.run(start_eva_server())


if __name__ == "__main__":
    # execute only if run as the entry point into the program
    main()
