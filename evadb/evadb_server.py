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
from signal import SIGTERM

from psutil import process_iter

"""
To allow running evadb_server from any location
"""
THIS_DIR = dirname(__file__)
EvaDB_CODE_DIR = abspath(join(THIS_DIR, ".."))
sys.path.append(EvaDB_CODE_DIR)

from evadb.server.server import EvaServer  # noqa: E402


async def start_evadb_server(
    db_dir: str, host: str, port: str, custom_db_uri: str = None
):
    """Start the evadb server"""
    evadb_server = EvaServer()
    await evadb_server.start_evadb_server(db_dir, host, port, custom_db_uri)


def stop_server():
    """
    Stop the evadb server
    """
    for proc in process_iter():
        if proc.name() == "evadb_server":
            proc.send_signal(SIGTERM)

    return 0


def main():
    parser = argparse.ArgumentParser(description="EvaDB Server")

    parser.add_argument(
        "--host",
        help="Specify the host address on which the server will start.",
    )

    parser.add_argument(
        "--port",
        help="Specify the port number on which the server will start.",
    )

    parser.add_argument(
        "--db_dir", help="Specify the evadb directory which the server should access."
    )

    parser.add_argument(
        "--sql_backend",
        help="Specify the custom sql database to use for structured data.",
    )

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

    args.host = args.host or "0.0.0.0"
    args.port = args.port or "8803"
    # Stop server
    if args.stop:
        return stop_server()

    # Start server
    if args.start:
        asyncio.run(
            start_evadb_server(args.db_dir, args.host, args.port, args.sql_backend)
        )


if __name__ == "__main__":
    # execute only if run as the entry point into the program
    main()
