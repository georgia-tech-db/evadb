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
from datetime import datetime
from decimal import Decimal
from typing import Callable, Iterable, List, TypeVar, Union

import numpy as np
import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.expression.abstract_expression import ExpressionType
from evadb.parser.alias import Alias
from evadb.utils.generic_utils import PickleSerializer
from evadb.utils.logging_manager import logger

Batch = TypeVar("Batch")


class Batch:
    """
    Data model used for storing a batch of frames.
    Internally stored as a pandas DataFrame with columns
    "id" and "data".
    id: integer index of frame
    data: frame as np.array

    Arguments:
        frames (DataFrame): pandas Dataframe holding frames data
    """

    def __init__(self, frames=None):
        self._frames = pd.DataFrame() if frames is None else frames
        if not isinstance(self._frames, pd.DataFrame):
            raise ValueError(
                "Batch constructor not properly called.\n"
                f"Expected pandas.DataFrame, got {type(self._frames)}"
            )

    @property
    def frames(self) -> pd.DataFrame:
        return self._frames

    def __len__(self):
        return len(self._frames)

    @property
    def columns(self):
        return list(self._frames.columns)

    def column_as_numpy_array(self, column_name: str) -> np.ndarray:
        """Return a column as numpy array

        Args:
            column_name (str): the name of the required column

        Returns:
            numpy.ndarray: the column data as a numpy array
        """
        return self._frames[column_name].to_numpy()

    def serialize(self):
        obj = {"frames": self._frames, "batch_size": len(self)}
        return PickleSerializer.serialize(obj)

    @classmethod
    def deserialize(cls, data):
        obj = PickleSerializer.deserialize(data)
        return cls(frames=obj["frames"])

    @classmethod
    def from_eq(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(pd.DataFrame(batch1.to_numpy() == batch2.to_numpy()))

    @classmethod
    def from_greater(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(pd.DataFrame(batch1.to_numpy() > batch2.to_numpy()))

    @classmethod
    def from_lesser(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(pd.DataFrame(batch1.to_numpy() < batch2.to_numpy()))

    @classmethod
    def from_greater_eq(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(pd.DataFrame(batch1.to_numpy() >= batch2.to_numpy()))

    @classmethod
    def from_lesser_eq(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(pd.DataFrame(batch1.to_numpy() <= batch2.to_numpy()))

    @classmethod
    def from_not_eq(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(pd.DataFrame(batch1.to_numpy() != batch2.to_numpy()))

    @classmethod
    def compare_contains(cls, batch1: Batch, batch2: Batch) -> None:
        return cls(
            pd.DataFrame(
                [all(x in p for x in q) for p, q in zip(left, right)]
                for left, right in zip(batch1.to_numpy(), batch2.to_numpy())
            )
        )

    @classmethod
    def compare_is_contained(cls, batch1: Batch, batch2: Batch) -> None:
        return cls(
            pd.DataFrame(
                [all(x in q for x in p) for p, q in zip(left, right)]
                for left, right in zip(batch1.to_numpy(), batch2.to_numpy())
            )
        )

    @classmethod
    def compare_like(cls, batch1: Batch, batch2: Batch) -> None:
        col = batch1._frames.iloc[:, 0]
        regex = batch2._frames.iloc[:, 0][0]
        return cls(pd.DataFrame(col.astype("str").str.match(pat=regex)))

    def __str__(self) -> str:
        with pd.option_context(
            "display.pprint_nest_depth", 1, "display.max_colwidth", 100
        ):
            return f"{self._frames}"

    def __eq__(self, other: Batch):
        # this function does not work if a column is a nested numpy arrays
        # (eg, bboxes from yolo).
        return self._frames[sorted(self.columns)].equals(
            other.frames[sorted(other.columns)]
        )

    def __getitem__(self, indices) -> Batch:
        """
        Returns a batch with the desired frames

        Arguments:
            indices (list, slice or mask): list must be
            a list of indices; mask is boolean array-like
            (i.e. list, NumPy array, DataFrame, etc.)
            of appropriate size with True for desired frames.
        """
        if isinstance(indices, list):
            return self._get_frames_from_indices(indices)
        elif isinstance(indices, slice):
            start = indices.start if indices.start else 0
            end = indices.stop if indices.stop else len(self.frames)
            if end < 0:
                end = len(self._frames) + end
            step = indices.step if indices.step else 1
            return self._get_frames_from_indices(range(start, end, step))
        elif isinstance(indices, int):
            return self._get_frames_from_indices([indices])
        else:
            raise TypeError("Invalid argument type: {}".format(type(indices)))

    def _get_frames_from_indices(self, required_frame_ids):
        new_frames = self._frames.iloc[required_frame_ids, :]
        new_batch = Batch(new_frames)
        return new_batch

    def apply_function_expression(self, expr: Callable) -> Batch:
        """
        Execute function expression on frames.
        """
        if hasattr(expr.forward, "tags"):
            input_tags = expr.forward.tags["input"][0]
            output_tags = expr.forward.tags["output"][0]
            self.drop_column_alias(metadata=(input_tags, output_tags))
        else:
            self.drop_column_alias()

        return Batch(expr(self._frames))

    def iterrows(self):
        return self._frames.iterrows()

    def sort(self, by=None) -> None:
        """
        in_place sort
        """
        if self.empty():
            return
        if by is None:
            by = self.columns[0]
        self._frames.sort_values(by=by, ignore_index=True, inplace=True)

    def sort_orderby(self, by, sort_type=None) -> None:
        """
        in_place sort for order_by

        Args:
            by: list of column names
            sort_type: list of True/False if ASC for each column name in 'by'
                i.e [True, False] means [ASC, DESC]
        """

        if sort_type is None:
            sort_type = [True]

        assert by is not None
        for column in by:
            assert (
                column in self._frames.columns
            ), "Can not orderby non-projected column: {}".format(column)

        self._frames.sort_values(
            by, ascending=sort_type, ignore_index=True, inplace=True
        )

    def invert(self) -> None:
        self._frames = ~self._frames

    def all_true(self) -> bool:
        return self._frames.all().bool()

    def all_false(self) -> bool:
        inverted = ~self._frames
        return inverted.all().bool()

    def create_mask(self) -> List:
        """
        Return list of indices of first row.
        """
        return self._frames[self._frames[0]].index.tolist()

    def create_inverted_mask(self) -> List:
        return self._frames[~self._frames[0]].index.tolist()

    def update_indices(self, indices: List, other: Batch):
        self._frames.iloc[indices] = other._frames
        self._frames = pd.DataFrame(self._frames)

    def file_paths(self) -> Iterable:
        yield from self._frames["file_path"]

    def project(self, cols: None) -> Batch:
        """
        Takes as input the column list, returns the projection.
        We do a copy for now.
        """
        cols = cols or []
        verified_cols = [c for c in cols if c in self._frames]
        unknown_cols = list(set(cols) - set(verified_cols))
        assert len(unknown_cols) == 0, unknown_cols
        return Batch(self._frames[verified_cols])

    @classmethod
    def merge_column_wise(cls, batches: List[Batch], auto_renaming=False) -> Batch:
        """
        Merge list of batch frames column_wise and return a new batch frame
        Arguments:
            batches: List[Batch]: list of batch objects to be merged
            auto_renaming: if true rename column names if required

        Returns:
            Batch: Merged batch object
        """
        if not len(batches):
            return Batch()

        frames = [batch.frames for batch in batches]

        # Check merging matched indices
        frames_index = [list(frame.index) for frame in frames]
        for i, frame_index in enumerate(frames_index):
            assert (
                frame_index == frames_index[i - 1]
            ), "Merging of DataFrames with unmatched indices can cause undefined behavior"

        new_frames = pd.concat(frames, axis=1, copy=False, ignore_index=False)
        if new_frames.columns.duplicated().any():
            logger.debug("Duplicated column name detected {}".format(new_frames))
        return Batch(new_frames)

    def __add__(self, other: Batch) -> Batch:
        """
        Adds two batch frames and return a new batch frame
        Arguments:
            other (Batch): other framebatch to add

        Returns:
            Batch
        """
        if not isinstance(other, Batch):
            raise TypeError("Input should be of type Batch")

        # Appending a empty dataframe with column name leads to NaN row.
        if self.empty():
            return other
        if other.empty():
            return self

        return Batch.concat([self, other], copy=False)

    @classmethod
    def concat(cls, batch_list: Iterable[Batch], copy=True) -> Batch:
        """Concat a list of batches.
        Notice: only frames are considered.
        """

        # pd.concat will convert generator into list, so it does not hurt
        # if we convert ourselves.
        frame_list = list([batch.frames for batch in batch_list])
        if len(frame_list) == 0:
            return Batch()
        frame = pd.concat(frame_list, ignore_index=True, copy=copy)

        return Batch(frame)

    @classmethod
    def stack(cls, batch: Batch, copy=True) -> Batch:
        """Stack a given batch along the 0th dimension.
        Notice: input assumed to contain only one column with video frames

        Returns:
            Batch (always of length 1)
        """
        if len(batch.columns) > 1:
            raise ValueError("Stack can only be called on single-column batches")
        frame_data_col = batch.columns[0]
        data_to_stack = batch.frames[frame_data_col].values.tolist()

        if isinstance(data_to_stack[0], np.ndarray) and len(data_to_stack[0].shape) > 1:
            # if data_to_stack has more than 1 axis, we add a new axis
            # [(3, 224, 224) * 10] -> (10, 3, 224, 224)
            stacked_array = np.array(batch.frames[frame_data_col].values.tolist())
        else:
            # we concatenate along the zeroth axis
            # this makes sense for audio and text
            stacked_array = np.hstack(batch.frames[frame_data_col].values)

        stacked_frame = pd.DataFrame([{frame_data_col: stacked_array}])
        return Batch(stacked_frame)

    @classmethod
    def join(cls, first: Batch, second: Batch, how="inner") -> Batch:
        return cls(
            first._frames.merge(
                second._frames, left_index=True, right_index=True, how=how
            )
        )

    @classmethod
    def combine_batches(
        cls, first: Batch, second: Batch, expression: ExpressionType
    ) -> Batch:
        """
        Creates Batch by combining two batches using some arithmetic expression.
        """
        if expression == ExpressionType.ARITHMETIC_ADD:
            return Batch(pd.DataFrame(first._frames + second._frames))
        elif expression == ExpressionType.ARITHMETIC_SUBTRACT:
            return Batch(pd.DataFrame(first._frames - second._frames))
        elif expression == ExpressionType.ARITHMETIC_MULTIPLY:
            return Batch(pd.DataFrame(first._frames * second._frames))
        elif expression == ExpressionType.ARITHMETIC_DIVIDE:
            return Batch(pd.DataFrame(first._frames / second._frames))

    def reassign_indices_to_hash(self, indices) -> None:
        """
        Hash indices and replace the indices with those hash values.
        """
        self._frames.index = self._frames[indices].apply(
            lambda x: hash(tuple(x)), axis=1
        )

    def aggregate(self, method: str) -> None:
        """
        Aggregate batch based on method.
        Methods can be sum, count, min, max, mean

        Arguments:
            method: string with one of the five above options
        """
        self._frames = self._frames.agg([method])

    def empty(self):
        """Checks if the batch is empty
        Returns:
            True if the batch_size == 0
        """
        return len(self) == 0

    def unnest(self, cols: List[str] = None) -> None:
        """
        Unnest columns and drop columns with no data
        """
        if cols is None:
            cols = list(self.columns)
        self._frames = self._frames.explode(cols)
        self._frames.dropna(inplace=True)

    def reverse(self) -> None:
        """Reverses dataframe"""
        self._frames = self._frames[::-1]
        self._frames.reset_index(drop=True, inplace=True)

    def drop_zero(self, outcomes: Batch) -> None:
        """Drop all columns with corresponding outcomes containing zero."""
        self._frames = self._frames[(outcomes._frames > 0).to_numpy()]

    def reset_index(self):
        """Resets the index of the data frame in the batch"""
        self._frames.reset_index(drop=True, inplace=True)

    def modify_column_alias(self, alias: Union[Alias, str]) -> None:
        # a, b, c -> table1.a, table1.b, table1.c
        # t1.a -> t2.a
        if isinstance(alias, str):
            alias = Alias(alias)
        new_col_names = []
        if len(alias.col_names):
            if len(self.columns) != len(alias.col_names):
                err_msg = (
                    f"Expected {len(alias.col_names)} columns {alias.col_names},"
                    f"got {len(self.columns)} columns {self.columns}."
                )
                raise RuntimeError(err_msg)
            new_col_names = [
                "{}.{}".format(alias.alias_name, col_name)
                for col_name in alias.col_names
            ]
        else:
            for col_name in self.columns:
                if "." in str(col_name):
                    new_col_names.append(
                        "{}.{}".format(alias.alias_name, str(col_name).split(".")[1])
                    )
                else:
                    new_col_names.append("{}.{}".format(alias.alias_name, col_name))

        self._frames.columns = new_col_names

    def drop_column_alias(self, metadata=None) -> None:
        # table1.a, table1.b, table1.c -> a, b, c

        new_col_names = []
        for col_name in self.columns:
            if isinstance(col_name, str) and "." in col_name:
                new_col_names.append(col_name.split(".")[1])
            else:
                new_col_names.append(col_name)
                # Iterate over each column in the dataframe
        self._frames.columns = new_col_names
        if metadata is not None:
            input_meta, output_meta = metadata
            defined_column_names = [entry for entry in input_meta.columns]
            defined_column_types = [entry for entry in input_meta.column_types]
            defined_column_shapes = [entry for entry in input_meta.column_shapes]
            column_rename_map = {}

            def is_shape_matching(data, expected_shape):
                """
                Check if the shape of the data matches the expected shape..
                """

                data_shape = data.shape
                if len(data_shape) != len(expected_shape):
                    return False

                for data_dim, expected_dim in zip(data_shape, expected_shape):
                    if expected_dim is not None and data_dim != expected_dim:
                        return False

                return True

            def get_basic_element(data):
                # Check if the data is iterable (but not a string, as strings are also iterable)
                if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
                    # If the data is empty, return None
                    if len(data) == 0:
                        return None
                    # Recursively get the first element
                    return get_basic_element(data[0])
                else:
                    # If the data is not iterable, return it as is
                    return data

            def deduce_and_map_type(element, check_type):
                python_type_to_ndarray_type = {
                    int: NdArrayType.INT64,  # Python's int is commonly mapped to NumPy's np.int64
                    float: NdArrayType.FLOAT64,  # Python's float maps to np.float64
                    bool: NdArrayType.BOOL,  # Python's bool maps to np.bool_
                    str: NdArrayType.STR,  # Python's str maps to np.str_
                    bytes: NdArrayType.UINT8,  # Python's bytes type maps to np.uint8 (common for byte data)
                    complex: NdArrayType.FLOAT64,  # Python's complex type maps to np.float64 (real part)
                    Decimal: NdArrayType.DECIMAL,  # Decimal maps to a Decimal type in your NdArrayType
                    datetime: NdArrayType.DATETIME,  # datetime maps to np.datetime64
                    np.int8: NdArrayType.INT8,
                    np.uint8: NdArrayType.UINT8,
                    np.int16: NdArrayType.INT16,
                    np.int32: NdArrayType.INT32,
                    np.int64: NdArrayType.INT64,
                    np.float32: NdArrayType.FLOAT32,
                    np.float64: NdArrayType.FLOAT64,
                    np.unicode_: NdArrayType.UNICODE,
                    np.str_: NdArrayType.STR,
                    np.bool_: NdArrayType.BOOL,
                    np.datetime64: NdArrayType.DATETIME,
                }
                flexible_type_mapping = {
                    NdArrayType.INT8: [
                        NdArrayType.INT16,
                        NdArrayType.INT32,
                        NdArrayType.INT64,
                        NdArrayType.FLOAT32,
                        NdArrayType.FLOAT64,
                    ],
                    NdArrayType.UINT8: [
                        NdArrayType.INT16,
                        NdArrayType.INT32,
                        NdArrayType.INT64,
                        NdArrayType.FLOAT32,
                        NdArrayType.FLOAT64,
                    ],
                    NdArrayType.INT16: [
                        NdArrayType.INT8,
                        NdArrayType.INT32,
                        NdArrayType.INT64,
                        NdArrayType.FLOAT32,
                        NdArrayType.FLOAT64,
                    ],
                    NdArrayType.INT32: [
                        NdArrayType.INT8,
                        NdArrayType.INT16,
                        NdArrayType.INT64,
                        NdArrayType.FLOAT32,
                        NdArrayType.FLOAT64,
                    ],
                    NdArrayType.INT64: [
                        NdArrayType.INT8,
                        NdArrayType.INT16,
                        NdArrayType.INT32,
                        NdArrayType.FLOAT32,
                        NdArrayType.FLOAT64,
                    ],
                    NdArrayType.FLOAT32: [
                        NdArrayType.FLOAT64,
                        NdArrayType.INT8,
                        NdArrayType.INT16,
                        NdArrayType.INT32,
                        NdArrayType.INT64,
                    ],
                    NdArrayType.FLOAT64: [
                        NdArrayType.FLOAT32,
                        NdArrayType.INT8,
                        NdArrayType.INT16,
                        NdArrayType.INT32,
                        NdArrayType.INT64,
                    ],
                }
                element_type = type(element)
                if isinstance(element, int):
                    return check_type in [
                        NdArrayType.INT16,
                        NdArrayType.INT32,
                        NdArrayType.INT64,
                        NdArrayType.FLOAT32,
                        NdArrayType.FLOAT64,
                    ]
                if isinstance(element, float):
                    return check_type in [NdArrayType.FLOAT32, NdArrayType.FLOAT64]

                # Special handling for numpy types
                if isinstance(element, np.generic):
                    element_type = np.dtype(type(element)).type
                deduced_type = python_type_to_ndarray_type.get(element_type)
                if deduced_type == check_type:
                    return True
                if (
                    deduced_type in flexible_type_mapping
                    and check_type in flexible_type_mapping[deduced_type]
                ):
                    return True

                return False

            for col_name in self.columns:
                match = False
                for i, def_name in enumerate(list(defined_column_names)):
                    # If the column name matches, keep it as is
                    if def_name == col_name:
                        column_rename_map[col_name] = col_name
                        defined_column_names.remove(col_name)
                        defined_column_types.pop(i)
                        defined_column_shapes.pop(i)
                        match = True
                # if the column name doesnt match
                if not match:
                    for i, def_name in enumerate(list(defined_column_names)):
                        # check if shape match
                        sample_data = self._frames[col_name].iloc[0]
                        if is_shape_matching(sample_data, defined_column_shapes[i]):
                            basic_element = get_basic_element(sample_data)
                            if deduce_and_map_type(
                                basic_element, defined_column_types[i]
                            ):
                                column_rename_map[col_name] = def_name
                                defined_column_names.remove(def_name)
                                defined_column_types.pop(i)
                                defined_column_shapes.pop(i)
                                break

            # Rename columns in the dataframe
            self._frames.rename(columns=column_rename_map, inplace=True)
            new_cols = []
            for col in self.columns:
                new_cols.append(col_name.split(".")[0] + "." + column_rename_map[col])
            self.columns = new_cols

    def to_numpy(self):
        return self._frames.to_numpy()

    def rename(self, columns) -> None:
        "Rename column names"
        self._frames.rename(columns=columns, inplace=True)
