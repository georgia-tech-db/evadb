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
import unittest

from mock import patch

from evadb.configuration.constants import EvaDB_DATABASE_DIR
from evadb.evadb_server import main, start_evadb_server


class EvaDBServerTest(unittest.IsolatedAsyncioTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @patch("evadb.evadb_server.start_evadb_server")
    @patch("asyncio.run")
    def test_main(self, mock_run, mock_start_evadb_server):
        main()
        mock_start_evadb_server.assert_called_once()
        mock_run.assert_called_once()

    @patch("evadb.evadb_server.start_evadb_server")
    @patch("asyncio.start_server")
    async def test_start_evadb_server(self, mock_start_evadb_server, mock_start):
        await start_evadb_server(EvaDB_DATABASE_DIR, "0.0.0.0", 8803)
        mock_start_evadb_server.assert_called_once()
