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
from unittest import TestCase

from mock import patch, MagicMock

from src.catalog.services.df_column_service import DatasetColumnService


class DatasetColumnServiceTest(TestCase):

    def test_create_should_create_all_columns(self):
        mocks = [MagicMock() for i in range(5)]
        service = DatasetColumnService()
        service.create_column(mocks)
        for mock in mocks:
            mock.save.assert_called_once()

    @patch('src.catalog.services.df_column_service.DataFrameColumn')
    def test_column_by_metadata_id_and_names_should_query_correctly(self,
                                                                    mocked):
        mocked.query.with_entities.return_value.filter \
            .return_value.all.return_value = [[1], [2], [3]]

        service = DatasetColumnService()
        actual = service.columns_by_dataset_id_and_names(123, ["a", "b"])
        expected = [1, 2, 3]
        self.assertEqual(actual, expected)
