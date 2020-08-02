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

from src.catalog.services.udf_service import UdfService

UDF_TYPE = 'classification'
UDF_IMPL_PATH = 'file1'
UDF_NAME = 'name'
UDF_ID = 123


class UdfServiceTest(TestCase):

    @patch("src.catalog.services.udf_service.UdfMetadata")
    def test_create_udf_should_create_model(self, mocked):
        service = UdfService()
        service.create_udf(UDF_NAME, UDF_IMPL_PATH, UDF_TYPE)
        mocked.assert_called_with(UDF_NAME, UDF_IMPL_PATH, UDF_TYPE)
        mocked.return_value.save.assert_called_once()

    @patch("src.catalog.services.udf_service.UdfMetadata")
    def test_udf_by_name_should_query_model_with_name(self, mocked):
        service = UdfService()
        expected = mocked.query.filter.return_value.one \
            .return_value

        actual = service.udf_by_name(UDF_NAME)
        mocked.query.filter.assert_called_with(
            mocked._name == UDF_NAME)
        mocked.query.filter.return_value.one.assert_called_once()
        self.assertEqual(actual, expected)

    @patch("src.catalog.services.udf_service.UdfMetadata")
    def test_udf_by_id_should_query_model_with_id(self, mocked):
        service = UdfService()
        expected = mocked.query.filter.return_value.one \
            .return_value
        actual = service.udf_by_id(UDF_ID)
        mocked.query.filter.assert_called_with(
            mocked._id == UDF_ID)
        mocked.query.filter.return_value.one.assert_called_once()
        self.assertEqual(actual, expected)

    @patch('src.catalog.services.udf_service.UdfService.udf_by_name')
    def test_udf_delete_by_name(self, mock_udf_by_name):
        mock_udf_by_name.return_value = MagicMock()
        actual = UdfService().delete_udf_by_name(UDF_NAME)
        mock_udf_by_name.assert_called_once_with(UDF_NAME)
        mock_udf_by_name.return_value.delete.assert_called_once()
        self.assertTrue(actual)

        mock_udf_by_name.reset_mock(return_value=True, side_effect=True)
        mock_udf_by_name.return_value = None
        actual = UdfService().delete_udf_by_name(UDF_NAME)
        mock_udf_by_name.assert_called_once_with(UDF_NAME)
        self.assertTrue(actual)

        mock_udf_by_name.reset_mock(return_value=True, side_effect=True)
        mock_udf_by_name.side_effect = [Exception]
        actual = UdfService().delete_udf_by_name(UDF_NAME)
        mock_udf_by_name.assert_called_once_with(UDF_NAME)
        self.assertFalse(actual)

        mock_udf_by_name.reset_mock(return_value=True, side_effect=True)
        mock_udf_by_name.return_value = MagicMock()
        mock_udf_by_name.return_value.delete.side_effect = [Exception]
        actual = UdfService().delete_udf_by_name(UDF_NAME)
        mock_udf_by_name.assert_called_once_with(UDF_NAME)
        mock_udf_by_name.return_value.delete.assert_called_once()
        self.assertFalse(actual)
