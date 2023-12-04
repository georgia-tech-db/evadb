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
from test.util import get_evadb_for_testing
from test.markers import pytesseract_skip_marker

from evadb.server.command_handler import execute_query_fetch_all


class PytesseractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()

        load_image_query = """LOAD IMAGE 'data/ocr/Example.jpg' INTO MyImage;"""

        execute_query_fetch_all(self.evadb, load_image_query)

    def tearDown(self) -> None:
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyImage;")

    @pytesseract_skip_marker
    def test_pytesseract_function(self):
        function_name = "PyTesseractOCRFunction"
        execute_query_fetch_all(self.evadb, f"DROP FUNCTION IF EXISTS {function_name};")

        create_function_query = f"""CREATE FUNCTION IF NOT EXISTS{function_name}
            IMPL 'evadb/functions/pytesseract_function.py';
        """
        execute_query_fetch_all(self.evadb, create_function_query)

        ocr_query = f"SELECT {function_name}(data) FROM MyImage;"
        output_batch = execute_query_fetch_all(self.evadb, ocr_query)
        self.assertEqual(1, len(output_batch))
