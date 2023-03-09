import numpy as np
import torch
import pandas as pd

from eva.io_descriptors.eva_arguments import EvaArgument
from eva.utils.errors import TypeException



class NumpyArray(EvaArgument):
    """EVA data type for Numpy Array"""

    def __init__(self, shape=None, dtype=None) -> None:
        super().__init__()
        self.shape = shape
        self.dtype = dtype

    def check_type(self, input_object) -> bool:
        if self.dtype:
            if self.dtype == "int32":
                return isinstance(input_object, np.ndarray) and (
                    input_object.dtype == np.int32
                )
            elif self.dtype == "float16":
                return isinstance(input_object, np.ndarray) and (
                    input_object.dtype == np.float16
                )
            elif self.dtype == "float32":
                return isinstance(input_object, np.ndarray) and (
                    input_object.dtype == np.float32
                )

        elif not self.dtype:
            return isinstance(input_object, np.ndarray)

    def convert_data_type(self, input_object: any):
        try:
            arr = np.asarray(input_object)
            if self.dtype == "int32":
                return arr.astype(np.int32)
            elif self.dtype == "float16":
                return arr.astype(np.float16)
            elif self.dtype == "float32":
                return arr.astype(np.float32)
            elif not self.dtype:
                return arr

        except Exception as e:
            raise TypeException(
                "Cannot convert the input object to the required type. Error message: "
                + str(e)
            )

    def check_shape(self, input_object) -> bool:
        if self.shape:
            if input_object.shape != self.shape:
                return False

        return True

    def reshape(self, input_object):
        try:
            return np.reshape(input_object, self.shape)

        except Exception as e:

            raise TypeException(
                "The input object cannot be reshaped to %s. Error is %s"
                % (self.shape, str(e))
            )

    def name(self):
        return "NumpyArray"



class PyTorchTensor(EvaArgument):
    """EVA data type for PyTorch Tensor"""

    def __init__(self, shape=None, dtype=None) -> None:
        super().__init__()
        self.shape = shape
        self.dtype = dtype

    def check_type(self, input_object) -> bool:
        if self.dtype:
            if self.dtype == "int32":
                return isinstance(input_object, torch.Tensor) and (
                    input_object.dtype == torch.int32
                )
            elif self.dtype == "float16":
                return isinstance(input_object, torch.Tensor) and (
                    input_object.dtype == torch.float16
                )
            elif self.dtype == "float32":
                return isinstance(input_object, torch.Tensor) and (
                    input_object.dtype == torch.float32
                )

        elif not self.dtype:
            return isinstance(input_object, torch.Tensor)

    def convert_data_type(self, input_object: any):
        try:

            if self.dtype == "int32":
                return input_object.to(torch.int32)
            elif self.dtype == "float16":
                return input_object.to(torch.float16)
            elif self.dtype == "float32":
                return input_object.to(torch.float32)
            elif not self.dtype:
                return input_object

        except Exception as e:
            raise TypeException(
                "Cannot convert the input object to the required type. Error: " + str(e)
            )

    def check_shape(self, input_object) -> bool:
        if self.shape:
            if input_object.shape != self.shape:
                return False

        return True

    def reshape(self, input_object: any):
        torch_tensor = None

        if isinstance(input_object, list):
            torch_tensor = torch.Tensor(input_object)
        elif isinstance(input_object, np.ndarray):
            torch_tensor = torch.from_numpy(input_object)
        elif isinstance(input_object, torch.Tensor):
            torch_tensor = input_object

        if torch_tensor == None:
            raise TypeException(
                "Argument type not recognized. Must be numpy array or list to be converted to Tensor"
            )

        try:
            return torch.reshape(input_object, self.shape)
        except Exception as e:
            raise TypeException(
                "Cannot be reshaped to required shape %s. Error: %s"
                % (self.shape, str(e))
            )

    def name(self):
        return "PyTorch Tensor"


class PandasDataframe(EvaArgument):
    """EVA data type for Pandas Dataframe"""

    def __init__(self, columns) -> None:
        super().__init__()
        self.columns = columns

    def check_shape(self, input_object: any, required_shape: tuple = None) -> bool:
        return True

    def check_column_names(self, input_object):
        obj_cols = list(input_object.columns)
        return obj_cols == self.columns

    def check_type(self, input_object) -> bool:
        return isinstance(input_object, pd.DataFrame)

    def is_output_columns_set(self):
        return not (self.columns is None)

    def name(self):
        return "PandasDataframe"
