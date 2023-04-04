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
from test.util import create_text_csv, file_remove

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


class HuggingFaceTests(unittest.TestCase):
    """
    The tests below essentially check for the output format returned by HF.
    We need to ensure that it is in the format that we expect.
    """

    def setUp(self) -> None:
        CatalogManager().reset()

        # Use DETRAC for HF Tests to test variety of models
        query = """LOAD VIDEO 'data/ua_detrac/ua_detrac.mp4' INTO DETRAC;"""
        execute_query_fetch_all(query)

        # Text CSV for testing HF Text Based Models
        self.csv_file_path = create_text_csv()

    def tearDown(self) -> None:
        execute_query_fetch_all("DROP TABLE IF EXISTS DETRAC;")
        file_remove(self.csv_file_path)

    def test_object_detection(self):
        udf_name = "HFObjectDetector"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'object-detection'
        """
        execute_query_fetch_all(create_udf_query)

        select_query = "SELECT HFObjectDetector(data) FROM DETRAC WHERE id < 10;"
        output = execute_query_fetch_all(select_query)
        output_frames = output.frames

        # Test that output has 3 columns
        self.assertEqual(len(output_frames.columns), 3)

        # Test that number of rows is equal to 10
        self.assertEqual(len(output.frames), 10)

        # Test that there exists a column with udf_name.score and each entry is a list of floats
        self.assertTrue(udf_name.lower() + ".score" in output_frames.columns)
        self.assertTrue(
            all(isinstance(x, list) for x in output.frames[udf_name.lower() + ".score"])
        )

        # Test that there exists a column with udf_name.label and each entry is a list of strings
        self.assertTrue(udf_name.lower() + ".label" in output_frames.columns)
        self.assertTrue(
            all(isinstance(x, list) for x in output.frames[udf_name.lower() + ".label"])
        )

        # Test that there exists a column with udf_name.box and each entry is a dictionary with 4 keys
        self.assertTrue(udf_name.lower() + ".box" in output_frames.columns)
        for bbox in output.frames[udf_name.lower() + ".box"]:
            self.assertTrue(isinstance(bbox, list))
            bbox = bbox[0]
            self.assertTrue(isinstance(bbox, dict))
            self.assertTrue(len(bbox) == 4)
            self.assertTrue("xmin" in bbox)
            self.assertTrue("ymin" in bbox)
            self.assertTrue("xmax" in bbox)
            self.assertTrue("ymax" in bbox)

    def test_image_classification(self):
        udf_name = "HFImageClassifier"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'image-classification'
        """
        execute_query_fetch_all(create_udf_query)

        select_query = f"SELECT {udf_name}(data) FROM DETRAC WHERE id < 10;"
        output = execute_query_fetch_all(select_query)

        # Test that output has 2 columns
        self.assertEqual(len(output.frames.columns), 2)

        # Test that there exists a column with udf_name.score and each entry is a list of floats
        self.assertTrue(udf_name.lower() + ".score" in output.frames.columns)
        self.assertTrue(
            all(isinstance(x, list) for x in output.frames[udf_name.lower() + ".score"])
        )

        # Test that there exists a column with udf_name.label and each entry is a list of strings
        self.assertTrue(udf_name.lower() + ".label" in output.frames.columns)
        self.assertTrue(
            all(isinstance(x, list) for x in output.frames[udf_name.lower() + ".label"])
        )

    def test_text_classification(self):
        create_table_query = """CREATE TABLE IF NOT EXISTS MyCSV (
                id INTEGER UNIQUE,
                comment TEXT(30)
            );"""
        execute_query_fetch_all(create_table_query)

        load_table_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyCSV;"""
        execute_query_fetch_all(load_table_query)

        udf_name = "HFTextClassifier"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'text-classification'
        """
        execute_query_fetch_all(create_udf_query)

        select_query = f"SELECT {udf_name}(comment) FROM MyCSV;"
        output = execute_query_fetch_all(select_query)

        # Test that output has 2 columns
        self.assertEqual(len(output.frames.columns), 2)

        # Test that there exists a column with udf_name.label and each entry is either "POSITIVE" or "NEGATIVE"
        self.assertTrue(udf_name.lower() + ".label" in output.frames.columns)
        self.assertTrue(
            all(
                x in ["POSITIVE", "NEGATIVE"]
                for x in output.frames[udf_name.lower() + ".label"]
            )
        )

        # Test that there exists a column with udf_name.score and each entry is a float
        self.assertTrue(udf_name.lower() + ".score" in output.frames.columns)
        self.assertTrue(
            all(
                isinstance(x, float) for x in output.frames[udf_name.lower() + ".score"]
            )
        )