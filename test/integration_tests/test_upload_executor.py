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

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all

from test.util import file_remove, PATH_PREFIX


class UploadExecutorTest(unittest.TestCase):

    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()

    def tearDown(self):
        pass

    # integration test
    def test_should_upload_video_to_location(self):
        query = """UPLOAD PATH 'dummy.avi' BLOB "b'AAAA'" INTO MyVideo
                   WITH FORMAT VIDEO;"""
        execute_query_fetch_all(query)
        expected_blob = "b'AAAA'"
        with open(os.path.join(PATH_PREFIX, 'dummy.avi'), 'rb') as f:
            bytes_read = f.read()
            actual_blob = str(base64.b64encode(bytes_read))
        self.assertEqual(actual_blob, expected_blob)

    def test_should_check_for_file_table_load(self):
        pass

    def test_should_check_that_file_exists_at_location(self):
        self.assertTrue(os.path.isfile(os.path.join(PATH_PREFIX, 'dummy.avi')))

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(UploadExecutorTest('test_should_upload_video_to_location'))
    suite.addTest(UploadExecutorTest(
        'test_should_check_that_file_exists_at_location'))
    unittest.TextTestRunner().run(suite)
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
    # unittest.main(LoadExecutorTest("test_should_load_video_in_table"))
