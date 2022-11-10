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
import time
import unittest
from test.util import create_sample_video, file_remove
from unittest.mock import MagicMock

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import handle_request
from eva.utils.timer import Timer

NUM_FRAMES = 10


class TimerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_timer(self):

        sleep_time = Timer()
        with sleep_time:
            time.sleep(5)

        self.assertTrue(sleep_time.total_elapsed_time < 5.2)
        self.assertTrue(sleep_time.total_elapsed_time > 4.9)

    def test_timer_with_query(self):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD FILE 'dummy.avi' INTO MyVideo;"""
        transport = MagicMock()
        transport.write = MagicMock(return_value="response_message")
        response = asyncio.run(handle_request(transport, load_query))
        self.assertTrue(response.error is None)
        self.assertTrue(response.query_time is not None)

        # If response is an error, we do not report time
        load_query = """LOAD INFILE 'dummy.avi' INTO MyVideo;"""
        transport = MagicMock()
        transport.write = MagicMock(return_value="response_message")
        response = asyncio.run(handle_request(transport, load_query))
        self.assertTrue(response.error is not None)
        self.assertTrue(response.query_time is None)

        file_remove("dummy.avi")
