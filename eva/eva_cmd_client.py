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
from eva.server.interpreter import start_cmd_client  # noqa: E402


async def eva_client():
    """
    Start the eva system
    """

    # Get the hostname and port information from the configuration file
    config = ConfigurationManager()
    host = config.get_value("server", "host")
    port = config.get_value("server", "port")

    # Launch client
    try:
        await start_cmd_client(host, port)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.critical(e)
        raise e


def main():
    asyncio.run(eva_client())


if __name__ == "__main__":
    main()
