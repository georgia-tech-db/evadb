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

from mock import MagicMock, patch

from evadb.catalog.catalog_type import NdArrayType
from evadb.executor.create_udf_executor import CreateUDFExecutor
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe


class CreateUdfExecutorTest(unittest.TestCase):
    @patch("evadb.executor.create_udf_executor.load_udf_class_from_file")
    def test_should_create_udf(self, load_udf_class_from_file_mock):
        catalog_instance = MagicMock()
        catalog_instance().get_udf_catalog_entry_by_name.return_value = None
        catalog_instance().insert_udf_catalog_entry.return_value = "udf"
        impl_path = MagicMock()
        abs_path = impl_path.absolute.return_value = MagicMock()
        abs_path.as_posix.return_value = "test.py"
        load_udf_class_from_file_mock.return_value.return_value = "mock_class"
        plan = type(
            "CreateUDFPlan",
            (),
            {
                "name": "udf",
                "if_not_exists": False,
                "inputs": ["inp"],
                "outputs": ["out"],
                "impl_path": impl_path,
                "udf_type": "classification",
                "metadata": {"key1": "value1", "key2": "value2"},
            },
        )
        evadb = MagicMock
        evadb.catalog = catalog_instance
        evadb.config = MagicMock()
        create_udf_executor = CreateUDFExecutor(evadb, plan)
        next(create_udf_executor.exec())
        catalog_instance().insert_udf_catalog_entry.assert_called_with(
            "udf",
            "test.py",
            "classification",
            ["inp", "out"],
            {"key1": "value1", "key2": "value2"},
        )

    @patch("evadb.executor.create_udf_executor.load_udf_class_from_file")
    def test_should_raise_error_on_incorrect_io_definition(
        self, load_udf_class_from_file_mock
    ):
        catalog_instance = MagicMock()
        catalog_instance().get_udf_catalog_entry_by_name.return_value = None
        catalog_instance().insert_udf_catalog_entry.return_value = "udf"
        impl_path = MagicMock()
        abs_path = impl_path.absolute.return_value = MagicMock()
        abs_path.as_posix.return_value = "test.py"
        load_udf_class_from_file_mock.return_value.return_value = "mock_class"
        incorrect_input_definition = PandasDataframe(
            columns=["Frame_Array", "Frame_Array_2"],
            column_types=[NdArrayType.UINT8],
            column_shapes=[(3, 256, 256), (3, 256, 256)],
        )
        load_udf_class_from_file_mock.return_value.forward.tags = {
            "input": [incorrect_input_definition],
            "output": [],
        }
        plan = type(
            "CreateUDFPlan",
            (),
            {
                "name": "udf",
                "if_not_exists": False,
                "inputs": [],
                "outputs": [],
                "impl_path": impl_path,
                "udf_type": "classification",
            },
        )
        evadb = MagicMock
        evadb.catalog = catalog_instance
        evadb.config = MagicMock()
        create_udf_executor = CreateUDFExecutor(evadb, plan)
        # check a string in the error message
        with self.assertRaises(RuntimeError) as exc:
            next(create_udf_executor.exec())
        self.assertIn(
            "Error creating UDF, input/output definition incorrect:", str(exc.exception)
        )

        catalog_instance().insert_udf_catalog_entry.assert_not_called()
