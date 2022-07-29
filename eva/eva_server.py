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
import sys
from os.path import abspath, dirname, join

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


def main():
    mode = ConfigurationManager().get_value("core", "mode")
    init_builtin_udfs(mode=mode)
    eva()


if __name__ == "__main__":
    # execute only if run as the entry point into the program
    main()
