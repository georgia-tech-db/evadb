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
from abc import abstractmethod
from typing import Tuple

from eva.catalog.catalog_type import ColumnType, Dimension, NdArrayType


class EvaArgument(object):
    """
    Base class for the data types that are used inside Eva. This class is inherited by the NumPyArray,
    PyTorchTensor and PandasDataFrame classes.
    The functions are implemented in the child classes.

    """

    @abstractmethod
    def __init__(
        self,
        name: str = None,
        type: ColumnType = None,
        is_nullable: bool = None,
        array_type: NdArrayType = None,
        array_dimensions: Tuple[int] = None,
    ) -> None:
        """The parameters like shape, data type are passed as parameters to be initialized

        Args:
            shape (tuple[int]): a tuple of integers of the required shape.
            dtype (str): datatype of the elements. Types are int32, float16 and float32.

        """
        self.shape = shape
        self.dtype = dtype
        self.columns = columns

    @abstractmethod
    def check_type(self, input_object: any) -> bool:
        """Checks the type of the input_object with

        Args:
            input_object (any): the object whose type should be checked. The required type is given in the constructor.

        Returns:
            bool: True if the type of input_object matches the required type. False otherwise.

        """
        pass

    @abstractmethod
    def check_shape(self, input_object: any, required_shape: tuple = None) -> bool:
        """Checks the shape of the input_object with

        Args:
            input_object (any): the object whose shape should be checked. The required shape is given in the constructor.

        Returns:
            bool: True if the shape of input_object matches the required type. False otherwise.

        """

        pass

    @abstractmethod
    def name(self):
        """Returns the name of the EvaArgument.

        It is used in the construction of the error messages.
        """
        pass

    @abstractmethod
    def is_output_columns_set(self):
        """Checks if the output columns are set.

        This is used for EvaArguments which are of PandasDataFrame type.

        """
        pass

    @abstractmethod
    def check_column_names(self, output_object):
        """Checks if the output column names match the required column names list.

        Args:
            output_object (any): the object whose columns should be checked. It should be of type PandasDataFrame.
                        The required column list is given in the constructor.

        Returns:
            bool: True if the column names of output_object matches the required columns list. False otherwise.

        """
        pass

    @abstractmethod
    def reshape(self, input_object: any):
        """function to reshape the input object to the required shape given in the constructor

        Args:
            input_object (any): the object which must be reshaped
        """
        pass

    @abstractmethod
    def convert_data_type(self, input_object: any):
        """convert the data type of input object to that given in the constructor.

        Args:
            input_object (any): object whose data type must be updated.
        """

    def is_shape_defined(self):
        """returns True if the size has been specified. False otherwise"""
        if self.shape is None:
            return False

        return True

    def is_dtype_defined(self):
        """returns True if the dtype has been specified. False otherwise"""
        if self.dtype is None:
            return False

        return True
