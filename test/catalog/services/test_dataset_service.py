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

from mock import patch

from eva.catalog.services.df_service import DatasetService

DATASET_ID = 123
DATASET_URL = "file1"
DATASET_NAME = "name"
DATABASE_NAME = "test"
IDENTIFIER = "data_id"
DATASET_NEW_NAME = "new_name"


class DatasetServiceTest(unittest.TestCase):
    @patch("eva.catalog.services.df_service.DataFrameMetadata")
    def test_create_dataset_should_create_model(self, mocked):
        service = DatasetService()
        service.create_dataset(DATASET_NAME, DATASET_URL, identifier_id=IDENTIFIER)
        mocked.assert_called_with(
            name=DATASET_NAME,
            file_url=DATASET_URL,
            identifier_id=IDENTIFIER,
            is_video=False,
        )
        mocked.return_value.save.assert_called_once()

    @patch("eva.catalog.services.df_service.DataFrameMetadata")
    def test_dataset_by_id_should_query_model_with_id(self, mocked):
        service = DatasetService()
        service.dataset_by_id(DATASET_ID)
        mocked.query.filter.assert_called_with(mocked._id == DATASET_ID)
        mocked.query.filter.return_value.one.assert_called_once()

    @patch("eva.catalog.services.df_service.DataFrameMetadata")
    def test_dataset_by_name_queries_model_with_name_and_return_id(self, mocked):
        service = DatasetService()

        expected_output = 1
        mocked.query.with_entities.return_value.filter.return_value.one.return_value = [
            expected_output
        ]

        result = service.dataset_by_name(DATASET_NAME)
        mocked.query.with_entities.assert_called_with(mocked._id)
        mocked.query.with_entities.return_value.filter.assert_called_with(
            mocked._name == DATASET_NAME
        )

        self.assertEqual(result, expected_output)

    @patch("eva.catalog.services.df_service.DataFrameMetadata")
    def test_dataset_object_by_name_queries_with_name_returns_model_object(
        self, mocked
    ):
        service = DatasetService()
        actual = service.dataset_object_by_name(DATABASE_NAME, DATASET_NAME)
        expected = mocked.query.filter.return_value.one_or_none.return_value

        self.assertEqual(actual, expected)

    @patch("eva.catalog.services.df_service.DatasetService.dataset_object_by_name")
    def test_rename_dataset_by_name(self, mock_func):
        service = DatasetService()
        service.rename_dataset_by_name(
            DATASET_NEW_NAME, "database_name", "dataset_name"
        )
        mock_func.assert_called_once_with("database_name", "dataset_name")
        mock_func.return_value.update.assert_called_once_with(_name=DATASET_NEW_NAME)

    def test_rename_dataset_by_name_should_raise_exception(self):
        with patch.object(DatasetService, "dataset_object_by_name") as mock_func:
            ERR_MSG = "err_message"
            mock_func.side_effect = Exception(ERR_MSG)
            service = DatasetService()
            with self.assertRaises(Exception) as cm:
                service.rename_dataset_by_name(
                    DATASET_NEW_NAME, DATABASE_NAME, DATASET_NAME
                )
            self.assertEqual(
                "Update dataset name failed for {} with error {}".format(
                    DATASET_NAME, ERR_MSG
                ),
                str(cm.exception),
            )
            mock_func.assert_called_once_with(DATABASE_NAME, DATASET_NAME)
            mock_func.return_value.update.assert_not_called()

    @patch("eva.catalog.services.df_service.DatasetService.dataset_object_by_name")
    def test_drop_dataset_by_name(self, mock_func):
        service = DatasetService()
        service.drop_dataset_by_name(DATABASE_NAME, DATASET_NAME)
        mock_func.assert_called_once_with(DATABASE_NAME, DATASET_NAME)
        mock_func.return_value.delete.assert_called_once()

    def test_drop_dataset_by_name_should_raise_exception(self):
        with patch.object(DatasetService, "dataset_object_by_name") as mock_func:
            ERR_MSG = "err_message"
            mock_func.side_effect = Exception(ERR_MSG)
            service = DatasetService()
            with self.assertRaises(Exception) as cm:
                service.drop_dataset_by_name(DATABASE_NAME, DATASET_NAME)
            self.assertEqual(
                "Delete dataset failed for name {} with error {}".format(
                    DATASET_NAME, ERR_MSG
                ),
                str(cm.exception),
            )
            mock_func.assert_called_once_with(DATABASE_NAME, DATASET_NAME)
            mock_func.return_value.delete.assert_not_called()
