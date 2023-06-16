# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.utils.logging_manager import logger

"""
To allow running evadb_server from any location
"""
THIS_DIR = dirname(__file__)
EvaDB_CODE_DIR = abspath(join(THIS_DIR, ".."))
sys.path.append(EvaDB_CODE_DIR)

from evadb.configuration.configuration_manager import ConfigurationManager  # noqa: E402
from evadb.server.interpreter import start_cmd_client  # noqa: E402


async def evadb_client(host: str, port: int):
    """
    Start the evadb client
    """

    # Launch client
    try:
        await start_cmd_client(host, port)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.critical(e)
        raise e


def main():
    parser = argparse.ArgumentParser(description="EvaDB Client")

    parser.add_argument(
        "--host",
        help="Specify the host address of the server you want to connect to.",
    )

    parser.add_argument(
        "--port",
        help="Specify the port number of the server you want to connect to.",
    )

    # PARSE ARGS
    args, unknown = parser.parse_known_args()

    host = (
        args.host if args.host else ConfigurationManager().get_value("server", "host")
    )

    port = (
        args.port if args.port else ConfigurationManager().get_value("server", "port")
    )
    asyncio.run(evadb_client(host, port))


if __name__ == "__main__":
    main()
