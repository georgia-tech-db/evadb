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
import os
import unittest
from test.util import (
    FRAME_SIZE,
    NUM_FRAMES,
    create_dummy_csv_batches,
    create_sample_csv,
    file_remove,
    upload_dir_from_config,
)

from eva.expression.tuple_value_expression import TupleValueExpression
from eva.readers.csv_reader import CSVReader


class CSVLoaderTest(unittest.TestCase):
    def setUp(self):
        create_sample_csv()

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
            file_url=os.path.join(upload_dir_from_config, "dummy.csv"),
            column_list=column_list,
            batch_mem_size=NUM_FRAMES * FRAME_SIZE,
        )

        # get the batches
        batches = list(csv_loader.read())
        expected = list(create_dummy_csv_batches())

        # assert batches are equal
        self.assertTrue(batches, expected)
