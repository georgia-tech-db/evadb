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

from mock import patch

from src.catalog.services.df_service import DatasetService

DATASET_ID = 123
DATASET_URL = 'file1'
DATASET_NAME = 'name'
DATABASE_NAME = "test"


class DatasetServiceTest(TestCase):

    @patch("src.catalog.services.df_service.DataFrameMetadata")
    def test_create_dataset_should_create_model(self, mocked):
        service = DatasetService()
        service.create_dataset(DATASET_NAME, DATASET_URL)
        mocked.assert_called_with(name=DATASET_NAME, file_url=DATASET_URL)
        mocked.return_value.save.assert_called_once()

    @patch("src.catalog.services.df_service.DataFrameMetadata")
    def test_dataset_by_id_should_query_model_with_id(self, mocked):
        service = DatasetService()
        service.dataset_by_id(DATASET_ID)
        mocked.query.filter.assert_called_with(
            mocked._id == DATASET_ID)
        mocked.query.filter.return_value.one.assert_called_once()

    @patch("src.catalog.services.df_service.DataFrameMetadata")
    def test_dataset_by_name_queries_model_with_name_and_return_id(self,
                                                                   mocked):
        service = DatasetService()

        expected_output = 1
        mocked.query.with_entities.return_value.filter.return_value.one \
            .return_value = [expected_output]

        result = service.dataset_by_name(DATASET_NAME)
        mocked.query.with_entities.assert_called_with(mocked._id)
        mocked.query.with_entities.return_value.filter.assert_called_with(
            mocked._name == DATASET_NAME)

        self.assertEqual(result, expected_output)

    @patch("src.catalog.services.df_service.DataFrameMetadata")
    def test_dataset_object_by_name_queries_with_name_returns_model_object(
            self,
            mocked):
        service = DatasetService()
        actual = service.dataset_object_by_name(DATABASE_NAME, DATASET_NAME)
        expected = mocked.query.filter.return_value.one.return_value

        self.assertEqual(actual, expected)
