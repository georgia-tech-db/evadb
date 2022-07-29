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

from mock import MagicMock, patch

from eva.catalog.services.df_column_service import DatasetColumnService


class DatasetColumnServiceTest(unittest.TestCase):
    def test_create_should_create_all_columns(self):
        mocks = [MagicMock() for i in range(5)]
        service = DatasetColumnService()
        service.create_column(mocks)
        for mock in mocks:
            mock.save.assert_called_once()

    @patch("eva.catalog.services.df_column_service.DataFrameColumn")
    def test_column_by_metadata_id_and_names_should_query_correctly(self, mocked):
        mocked.query.filter.return_value.all.return_value = [1, 2, 3]

        service = DatasetColumnService()
        metadata_id = 123
        column_names = ["a", "b"]
        actual = service.columns_by_dataset_id_and_names(metadata_id, column_names)
        mocked.query.filter.assert_called_with(
            mocked._metadata_id == metadata_id, mocked._name.in_(column_names)
        )
        expected = [1, 2, 3]

        self.assertEqual(actual, expected)

    @patch("eva.catalog.services.df_column_service.DataFrameColumn")
    def test_column_by_metadata_id_and_col_ids_should_query_correctly(self, mocked):
        return_val = [1, 2, 3]
        mocked.query.filter.return_value.all.return_value = return_val

        service = DatasetColumnService()
        metadata_id = 123
        column_ids = [1, 2]
        actual = service.columns_by_id_and_dataset_id(metadata_id, column_ids)
        mocked.query.filter.assert_called_with(
            mocked._metadata_id == metadata_id, mocked._id.in_(column_ids)
        )
        self.assertEqual(actual, return_val)

    @patch("eva.catalog.services.df_column_service.DataFrameColumn")
    def test_by_dataset_id_and_empty_col_ids_should_query_correctly(self, mocked):
        return_val = [1, 2, 3]
        mocked.query.filter.return_value.all.return_value = return_val

        service = DatasetColumnService()
        metadata_id = 123
        column_ids = None
        actual = service.columns_by_id_and_dataset_id(metadata_id, column_ids)
        mocked.query.filter.assert_called_with(mocked._metadata_id == metadata_id)
        self.assertEqual(actual, return_val)
