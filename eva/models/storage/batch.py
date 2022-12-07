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
from typing import Callable, Iterable, List, TypeVar, Union

import numpy as np
import pandas as pd

from eva.expression.abstract_expression import ExpressionType
from eva.parser.alias import Alias
from eva.utils.generic_utils import PickleSerializer
from eva.utils.logging_manager import logger

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
                "Batch constructor not properly called.\n" "Expected pandas.DataFrame"
            )

    @property
    def frames(self) -> pd.DataFrame:
        return self._frames

    def __len__(self):
        return len(self._frames)

    @property
    def columns(self):
        return self._frames.columns

    def column_as_numpy_array(self, column_name="data"):
        return np.array(self._frames[column_name])

    def serialize(self):
        obj = {"frames": self._frames, "batch_size": len(self)}
        return PickleSerializer.serialize(obj)

    @classmethod
    def deserialize(cls, data):
        obj = PickleSerializer.deserialize(data)
        return cls(frames=obj["frames"])

    @classmethod
    def from_eq(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(
            pd.DataFrame(batch1._frames.to_numpy() == batch2._frames.to_numpy())
        )

    @classmethod
    def from_greater(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(
            pd.DataFrame(batch1._frames.to_numpy() > batch2._frames.to_numpy())
        )

    @classmethod
    def from_lesser(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(
            pd.DataFrame(batch1._frames.to_numpy() < batch2._frames.to_numpy())
        )

    @classmethod
    def from_greater_eq(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(
            pd.DataFrame(batch1._frames.to_numpy() >= batch2._frames.to_numpy())
        )

    @classmethod
    def from_lesser_eq(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(
            pd.DataFrame(batch1._frames.to_numpy() <= batch2._frames.to_numpy())
        )

    @classmethod
    def from_not_eq(cls, batch1: Batch, batch2: Batch) -> Batch:
        return Batch(
            pd.DataFrame(batch1._frames.to_numpy() != batch2._frames.to_numpy())
        )

    @classmethod
    def compare_contains(cls, batch1: Batch, batch2: Batch) -> None:
        return cls(
            pd.DataFrame(
                [all(x in p for x in q) for p, q in zip(left, right)]
                for left, right in zip(
                    batch1._frames.to_numpy(), batch2._frames.to_numpy()
                )
            )
        )

    @classmethod
    def compare_is_contained(cls, batch1: Batch, batch2: Batch) -> None:
        return cls(
            pd.DataFrame(
                [all(x in q for x in p) for p, q in zip(left, right)]
                for left, right in zip(
                    batch1._frames.to_numpy(), batch2._frames.to_numpy()
                )
            )
        )

    def __str__(self) -> str:
        with pd.option_context(
            "display.pprint_nest_depth", 1, "display.max_colwidth", 100
        ):
            return f"{self._frames}"

    def __eq__(self, other: Batch):
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

    def apply_function_expression(self, expr: Callable) -> None:
        """
        Execute function expression on frames.
        """
        self._frames = expr(self._frames)

    def sort(self, by=None) -> None:
        """
        in_place sort
        """
        if by is None:
            if not self.empty():
                by = self.columns[0]
            else:
                logger.warn("Sorting an empty batch")
                return
        self._frames.sort_values(by=by, ignore_index=True, inplace=True)

    def sort_orderby(self, by, sort_type=None) -> None:
        """
        in_place sort for orderby

        Args:
            by: list of column names
            sort_type: list of True/False if ASC for each column name in 'by'
                i.e [True, False] means [ASC, DESC]
        """

        if sort_type is None:
            sort_type = [True]

        if by is not None:
            for column in by:
                if column not in self._frames.columns:
                    logger.error(
                        "Can not orderby non-projected column: {}".format(column)
                    )
                    raise KeyError(
                        "Can not orderby non-projected column: {}".format(column)
                    )

            self._frames.sort_values(
                by, ascending=sort_type, ignore_index=True, inplace=True
            )
        else:
            logger.warn("Columns and Sort Type are required for orderby")

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

    def video_file_paths(self) -> Iterable:
        yield from self._frames["video_file_path"]

    def project(self, cols: None) -> Batch:
        """
        Takes as input the column list, returns the projection.
        We do a copy for now.
        """
        cols = cols or []
        verfied_cols = [c for c in cols if c in self._frames]
        unknown_cols = list(set(cols) - set(verfied_cols))
        if len(unknown_cols):
            logger.warn(
                "Unexpected columns %s\n\
                                 Frames: %s"
                % (unknown_cols, self._frames)
            )
        return Batch(self._frames[verfied_cols])

    def repeat(self, times: int) -> None:
        """
        Repeat the rows of a dataframe.

        Arguments:
            times: number of times to repeat
        """
        self._frames = pd.DataFrame(np.repeat(self._frames.to_numpy(), times, axis=0))

    @classmethod
    def merge_column_wise(cls, batches: List[Batch], auto_renaming=False) -> Batch:
        """
        Merge list of batch frames column_wise and return a new batch frame
        Arguments:
            batches: List[Batch]: lsit of batch objects to be merged
            auto_renaming: if true rename column names if required

        Returns:
            Batch: Merged batch object
        """

        if not len(batches):
            return Batch()
        frames = [batch.frames for batch in batches]
        new_frames = pd.concat(frames, axis=1, copy=False)
        if new_frames.columns.duplicated().any():
            logger.warn("Duplicated column name detected {}".format(new_frames))
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

        new_frames = self._frames.append(other.frames, ignore_index=True)

        return Batch(new_frames)

    @classmethod
    def concat(cls, batch_list: Iterable[Batch], copy=True) -> Batch:
        """Concat a list of batches. Avoid the extra copying overhead by
        the append operation in __add__.
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

        stacked_array = np.array(batch.frames[frame_data_col].values.tolist())
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

    def unnest(self) -> None:
        """
        Unnest columns and drop columns with no data
        """
        self._frames = self._frames.explode(list(self._frames.columns))
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
                logger.error(err_msg)
                raise RuntimeError(err_msg)
            new_col_names = [
                "{}.{}".format(alias.alias_name, col_name)
                for col_name in alias.col_names
            ]
        else:
            for col_name in self.columns:
                if "." in col_name:
                    new_col_names.append(
                        "{}.{}".format(alias.alias_name, col_name.split(".")[1])
                    )
                else:
                    new_col_names.append("{}.{}".format(alias.alias_name, col_name))

        self._frames.columns = new_col_names

    def drop_column_alias(self) -> None:
        # table1.a, table1.b, table1.c -> a, b, c
        new_col_names = []
        for col_name in self.columns:
            if "." in col_name:
                new_col_names.append(col_name.split(".")[1])
            else:
                new_col_names.append(col_name)

        self._frames.columns = new_col_names
