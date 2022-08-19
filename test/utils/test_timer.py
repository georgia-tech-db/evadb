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

import unittest

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all
from eva.utils.timer import start_timer, end_timer, elapsed_time
from test.util import create_sample_video, file_remove

NUM_FRAMES = 10


class TimerTests(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_timer(self):

        start_timer()
        end_timer()
        t1 = elapsed_time()

        self.assertTrue(t1 < 5)

        start_timer()
        end_timer()
        t2 = elapsed_time("abc", False)

        self.assertTrue(t2 < 10)

    def test_timer_with_query(self):

        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD FILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)
        file_remove('dummy.avi')

