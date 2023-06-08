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

from evadb.catalog.catalog_type import ColumnType, Dimension, NdArrayType
from evadb.udfs.decorators.io_descriptors.data_types import (
    NumpyArray,
    PandasDataframe,
    PyTorchTensor,
)
from evadb.utils.errors import UDFIODefinitionError


class UDFIODescriptorsTests(unittest.TestCase):
    def test_catalog_entry_for_numpy_entry(self):
        numpy_array = NumpyArray(
            name="input", is_nullable=False, type=NdArrayType.UINT8, dimensions=(2, 2)
        )
        catalog_entries = numpy_array.generate_catalog_entries()

        # check that there is only a single catalog entry
        self.assertEqual(len(catalog_entries), 1)

        # check that the attributes of the catalog entry are correct
        catalog_entry = catalog_entries[0]
        self.assertEqual(catalog_entry.name, "input")
        self.assertEqual(catalog_entry.type, ColumnType.NDARRAY)
        self.assertEqual(catalog_entry.is_nullable, False)
        self.assertEqual(catalog_entry.array_type, NdArrayType.UINT8)
        self.assertEqual(catalog_entry.array_dimensions, (2, 2))
        self.assertEqual(catalog_entry.is_input, False)

    def test_catalog_entry_for_pytorch_entry(self):
        pytorch_tensor = PyTorchTensor(
            name="input", is_nullable=False, type=NdArrayType.UINT8, dimensions=(2, 2)
        )
        catalog_entries = pytorch_tensor.generate_catalog_entries()

        # check that there is only a single catalog entry
        self.assertEqual(len(catalog_entries), 1)

        # check that the attributes of the catalog entry are correct
        catalog_entry = catalog_entries[0]
        self.assertEqual(catalog_entry.name, "input")
        self.assertEqual(catalog_entry.type, ColumnType.NDARRAY)
        self.assertEqual(catalog_entry.is_nullable, False)
        self.assertEqual(catalog_entry.array_type, NdArrayType.UINT8)
        self.assertEqual(catalog_entry.array_dimensions, (2, 2))
        self.assertEqual(catalog_entry.is_input, False)

    def test_catalog_entry_for_pandas_entry_with_single_column_simple(self):
        # dataframe has only columns defined
        pandas_dataframe = PandasDataframe(columns=["Frame_Array"])
        catalog_entries = pandas_dataframe.generate_catalog_entries()

        # check that there is only a single catalog entry
        self.assertEqual(len(catalog_entries), 1)

        # check that the attributes of the catalog entry are correct
        catalog_entry = catalog_entries[0]
        self.assertEqual(catalog_entry.name, "Frame_Array")
        self.assertEqual(catalog_entry.type, ColumnType.NDARRAY)
        self.assertEqual(catalog_entry.is_nullable, False)
        self.assertEqual(catalog_entry.array_type, NdArrayType.ANYTYPE)
        self.assertEqual(catalog_entry.array_dimensions, Dimension.ANYDIM)

    def test_catalog_entry_for_pandas_entry_with_single_column(self):
        pandas_dataframe = PandasDataframe(
            columns=["Frame_Array"],
            column_types=[NdArrayType.UINT8],
            column_shapes=[(3, 256, 256)],
        )
        catalog_entries = pandas_dataframe.generate_catalog_entries()

        # check that there is only a single catalog entry
        self.assertEqual(len(catalog_entries), 1)

        # check that the attributes of the catalog entry are correct
        catalog_entry = catalog_entries[0]
        self.assertEqual(catalog_entry.name, "Frame_Array")
        self.assertEqual(catalog_entry.type, ColumnType.NDARRAY)
        self.assertEqual(catalog_entry.is_nullable, False)
        self.assertEqual(catalog_entry.array_type, NdArrayType.UINT8)
        self.assertEqual(catalog_entry.array_dimensions, (3, 256, 256))
        self.assertEqual(catalog_entry.is_input, False)

    def test_catalog_entry_for_pandas_entry_with_multiple_columns_simple(self):
        # dataframe has only columns defined
        pandas_dataframe = PandasDataframe(columns=["Frame_Array", "Frame_Array_2"])
        catalog_entries = pandas_dataframe.generate_catalog_entries()

        # check that there is only a single catalog entry
        self.assertEqual(len(catalog_entries), 2)

        # check that the attributes of the catalog entry are correct
        catalog_entry = catalog_entries[0]
        self.assertEqual(catalog_entry.name, "Frame_Array")
        self.assertEqual(catalog_entry.type, ColumnType.NDARRAY)
        self.assertEqual(catalog_entry.is_nullable, False)
        self.assertEqual(catalog_entry.array_type, NdArrayType.ANYTYPE)
        self.assertEqual(catalog_entry.array_dimensions, Dimension.ANYDIM)

        catalog_entry = catalog_entries[1]
        self.assertEqual(catalog_entry.name, "Frame_Array_2")
        self.assertEqual(catalog_entry.type, ColumnType.NDARRAY)
        self.assertEqual(catalog_entry.is_nullable, False)
        self.assertEqual(catalog_entry.array_type, NdArrayType.ANYTYPE)
        self.assertEqual(catalog_entry.array_dimensions, Dimension.ANYDIM)

    def test_catalog_entry_for_pandas_entry_with_multiple_columns(self):
        pandas_dataframe = PandasDataframe(
            columns=["Frame_Array", "Frame_Array_2"],
            column_types=[NdArrayType.UINT8, NdArrayType.FLOAT32],
            column_shapes=[(3, 256, 256), (3, 256, 256)],
        )
        catalog_entries = pandas_dataframe.generate_catalog_entries()

        # check that there is only a single catalog entry
        self.assertEqual(len(catalog_entries), 2)

        # check that the attributes of the catalog entry are correct
        catalog_entry = catalog_entries[0]
        self.assertEqual(catalog_entry.name, "Frame_Array")
        self.assertEqual(catalog_entry.type, ColumnType.NDARRAY)
        self.assertEqual(catalog_entry.is_nullable, False)
        self.assertEqual(catalog_entry.array_type, NdArrayType.UINT8)
        self.assertEqual(catalog_entry.array_dimensions, (3, 256, 256))
        self.assertEqual(catalog_entry.is_input, False)

        catalog_entry = catalog_entries[1]
        self.assertEqual(catalog_entry.name, "Frame_Array_2")
        self.assertEqual(catalog_entry.type, ColumnType.NDARRAY)
        self.assertEqual(catalog_entry.is_nullable, False)
        self.assertEqual(catalog_entry.array_type, NdArrayType.FLOAT32)
        self.assertEqual(catalog_entry.array_dimensions, (3, 256, 256))
        self.assertEqual(catalog_entry.is_input, False)

    def test_raises_error_on_incorrect_pandas_definition(self):
        # the dataframe should have multiple columns but column_types should be defined for only one
        pandas_dataframe = PandasDataframe(
            columns=["Frame_Array", "Frame_Array_2"],
            column_types=[NdArrayType.UINT8],
            column_shapes=[(3, 256, 256), (3, 256, 256)],
        )
        with self.assertRaises(UDFIODefinitionError):
            pandas_dataframe.generate_catalog_entries()
