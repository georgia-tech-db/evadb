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
from unittest import TestCase

from mock import MagicMock, patch

from eva.catalog.services.udf_io_service import UdfIOService

UDF_TYPE = "classification"
UDF_IMPL_PATH = "file1"
UDF_NAME = "name"
UDF_ID = 123


class UdfServiceTest(TestCase):
    @patch("eva.catalog.services.udf_io_service.UdfIO")
    def test_get_inputs_by_udf_id_should_query_model_with_id(self, mocked):
        service = UdfIOService()

        actual = service.get_inputs_by_udf_id(UDF_NAME)
        mocked.query.filter.assert_called_with(
            mocked._id == UDF_ID, mocked._is_input == True  # noqa
        )
        mocked.query.filter.return_value.all.assert_called_once()
        expected = mocked.query.filter.return_value.all.return_value
        self.assertEqual(actual, expected)

    @patch("eva.catalog.services.udf_io_service.UdfIO")
    def test_get_inputs_by_udf_id_should_raise(self, mock):
        service = UdfIOService()
        mock.query.filter.side_effect = Exception("error")
        with self.assertRaises(Exception) as cm:
            service.get_inputs_by_udf_id(UDF_NAME)
        self.assertEqual(
            f"Getting inputs for UDF id {UDF_NAME} raised error", str(cm.exception)
        )

    @patch("eva.catalog.services.udf_io_service.UdfIO")
    def test_get_outputs_by_udf_id_should_query_model_with_id(self, mocked):
        service = UdfIOService()

        actual = service.get_outputs_by_udf_id(UDF_NAME)
        mocked.query.filter.assert_called_with(
            mocked._id == UDF_ID, mocked._is_input == True  # noqa
        )
        mocked.query.filter.return_value.all.assert_called_once()
        expected = mocked.query.filter.return_value.all.return_value
        self.assertEqual(actual, expected)

    @patch("eva.catalog.services.udf_io_service.UdfIO")
    def test_get_outputs_by_udf_id_should_raise(self, mock):
        service = UdfIOService()
        mock.query.filter.side_effect = Exception("error")
        with self.assertRaises(Exception) as cm:
            service.get_outputs_by_udf_id(UDF_NAME)
        self.assertEqual(
            f"Getting outputs for UDF id {UDF_NAME} raised error", str(cm.exception)
        )

    def test_add_udf_io_should_save_io(self):
        service = UdfIOService()
        io_list = [MagicMock(), MagicMock()]
        service.add_udf_io(io_list)
        for mock in io_list:
            mock.save.assert_called_once()
