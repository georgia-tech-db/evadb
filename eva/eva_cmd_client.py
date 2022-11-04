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


def eva_client(host="0.0.0.0", port=5432):
    """
    Start the eva system
    """

    # Sets up logger
    config = ConfigurationManager()  # noqa: F841

    # Launch server
    try:
        start_cmd_client(host=host, port=port)
    except Exception as e:
        logger.critical(e)


def parse_args(args):
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-H",
        "--host",
        dest="host",
        type=str,
        help="Host address for EVA server",
        default="0.0.0.0",
    )
    parser.add_argument(
        "-P", "--port", dest="port", type=int, help="Port for EVA server", default=5432
    )
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    eva_client(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
