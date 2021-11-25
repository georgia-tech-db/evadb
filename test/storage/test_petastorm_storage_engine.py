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
import shutil
import unittest

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.storage.petastorm_storage_engine import PetastormStorageEngine
from eva.catalog.models.df_column import DataFrameColumn
from eva.catalog.column_type import ColumnType, NdArrayType

from test.util import create_dummy_batches
from test.util import NUM_FRAMES


class PetastormStorageEngineTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = None

    def create_sample_table(self):
        table_info = DataFrameMetadata("dataset", 'dataset')
        column_1 = DataFrameColumn("id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn(
            "data", ColumnType.NDARRAY, False, NdArrayType.UINT8, [
                2, 2, 3])
        table_info.schema = [column_1, column_2]
        return table_info

    def setUp(self):
        self.table = self.create_sample_table()

    def tearDown(self):
        try:
            shutil.rmtree('dataset', ignore_errors=True)
        except ValueError:
            pass

    def test_should_create_empty_table(self):
        petastorm = PetastormStorageEngine()
        petastorm.create(self.table)
        records = list(petastorm.read(self.table, batch_mem_size=3000))
        self.assertEqual(records, [])

    def test_should_write_rows_to_table(self):
        dummy_batches = list(create_dummy_batches())

        petastorm = PetastormStorageEngine()
        petastorm.create(self.table)
        for batch in dummy_batches:
            petastorm.write(self.table, batch)

        read_batch = list(petastorm.read(self.table, batch_mem_size=3000))
        self.assertTrue(read_batch, dummy_batches)

    def test_should_return_even_frames(self):
        dummy_batches = list(create_dummy_batches())

        petastorm = PetastormStorageEngine()
        petastorm.create(self.table)
        for batch in dummy_batches:
            petastorm.write(self.table, batch)

        read_batch = list(
            petastorm.read(
                self.table,
                batch_mem_size=3000,
                columns=["id"],
                predicate_func=lambda id: id %
                2 == 0))
        expected_batch = list(create_dummy_batches(
            filters=[
                i for i in range(NUM_FRAMES) if i %
                2 == 0]))
        self.assertTrue(read_batch, expected_batch)
