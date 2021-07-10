# coding=utf-8
# Copyright 2018-2020 EVA
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
import os
import base64

from src.server.command_handler import execute_query_fetch_all

from test.util import file_remove, PATH_PREFIX


class UploadExecutorTest(unittest.TestCase):

    def setUp(self):
        # reset the catalog manager before running each test
        pass

    def tearDown(self):
        file_remove('dummy.avi')

    # integration test
    def test_should_upload_video_to_location(self):
        query = """UPLOAD PATH 'dummy.avi' BLOB "b'AAAA'";"""
        execute_query_fetch_all(query)
        expected_blob = "b'AAAA'"
        with open(os.path.join(PATH_PREFIX, 'dummy.avi'), 'rb') as f:
            bytes_read = f.read()
            actual_blob = str(base64.b64encode(bytes_read))
        self.assertEqual(actual_blob, expected_blob)
