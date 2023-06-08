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
from test.util import create_dummy_csv_batches, create_sample_csv, file_remove

from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.readers.csv_reader import CSVReader


class CSVLoaderTest(unittest.TestCase):
    def setUp(self):
        self.csv_file_path = create_sample_csv()

    def tearDown(self):
        file_remove("dummy.csv")

    def test_should_return_one_batch(self):
        column_list = [
            TupleValueExpression(col_name="id", table_alias="dummy"),
            TupleValueExpression(col_name="frame_id", table_alias="dummy"),
            TupleValueExpression(col_name="video_id", table_alias="dummy"),
        ]

        # call the CSVReader
        csv_loader = CSVReader(
            file_url=self.csv_file_path,
            column_list=column_list,
        )

        # get the batches
        batches = list(csv_loader.read())
        expected = list(
            create_dummy_csv_batches(target_columns=["id", "frame_id", "video_id"])
        )

        # assert batches are equal
        self.assertEqual(batches, expected)
