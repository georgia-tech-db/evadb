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
import json
from typing import Iterable, List, TypeVar, Union

import numpy as np
import pandas as pd

from eva.parser.alias import Alias
from eva.utils.logging_manager import logger


class BatchEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return {"__dataframe__": obj.to_json()}
        return json.JSONEncoder.default(self, obj)


def as_batch(d):
    if "__dataframe__" in d:
        return pd.read_json(d["__dataframe__"], convert_dates=False)
    else:
        return d


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
        identifier_column (str): A column used to uniquely a row
    """

    def __init__(self, frames=None, identifier_column=None):
        self._frames = pd.DataFrame() if frames is None else frames
        if not isinstance(self._frames, pd.DataFrame):
            raise ValueError(
                "Batch constructor not properly called.\n" "Expected pandas.DataFrame"
            )
        self._identifier_column = identifier_column

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

    def to_json(self):
        obj = {
            "frames": self.frames,
            "batch_size": len(self),
            "identifier_column": self._identifier_column,
        }
        return json.dumps(obj, cls=BatchEncoder)

    @classmethod
    def from_json(cls, json_str: str):
        obj = json.loads(json_str, object_hook=as_batch)
        return cls(frames=obj["frames"], identifier_column=obj["identifier_column"])

    def __str__(self) -> str:
        return (
            "Batch Object:\n"
            "@dataframe: %s\n"
            "@batch_size: %d\n"
            "@identifier_column: %s"
            % (self._frames, len(self), self._identifier_column)
        )

    def __eq__(self, other: Batch):
        return self.frames[sorted(self.frames.columns)].equals(
            other.frames[sorted(other.frames.columns)]
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
                end = len(self.frames) + end
            step = indices.step if indices.step else 1
            return self._get_frames_from_indices(range(start, end, step))
        elif isinstance(indices, int):
            return self._get_frames_from_indices([indices])
        else:
            raise TypeError("Invalid argument type: {}".format(type(indices)))

    def _get_frames_from_indices(self, required_frame_ids):
        new_frames = self.frames.iloc[required_frame_ids, :]
        new_batch = Batch(new_frames)
        return new_batch

    def sort(self, by=None) -> None:
        """
        in_place sort
        """
        if by is None:
            if self._identifier_column in self._frames:
                by = [self._identifier_column]
            elif not self.empty():
                by = self.frames.columns[0]
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
        # if by is None and self.identifier_column in self._frames:
        #     by = [self.identifier_column]

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
        return Batch(self._frames[verfied_cols], self._identifier_column)

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

        new_frames = self.frames.append(other.frames, ignore_index=True)

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

    def empty(self):
        """Checks if the batch is empty
        Returns:
            True if the batch_size == 0
        """
        return len(self) == 0

    def reverse(self) -> None:
        """Reverses dataframe"""
        self._frames = self._frames[::-1]
        self._frames.reset_index(drop=True, inplace=True)

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
            if len(self.frames.columns) != len(alias.col_names):
                err_msg = (
                    f"Expected {len(alias.col_names)} columns {alias.col_names},"
                    f"got {len(self.frames.columns)} columns {self.frames.columns}."
                )
                logger.error(err_msg)
                raise RuntimeError(err_msg)
            new_col_names = [
                "{}.{}".format(alias.alias_name, col_name)
                for col_name in alias.col_names
            ]
        else:
            for col_name in self.frames.columns:
                if "." in col_name:
                    new_col_names.append(
                        "{}.{}".format(alias.alias_name, col_name.split(".")[1])
                    )
                else:
                    new_col_names.append("{}.{}".format(alias.alias_name, col_name))

        self.frames.columns = new_col_names

    def drop_column_alias(self) -> None:
        # table1.a, table1.b, table1.c -> a, b, c
        new_col_names = []
        for col_name in self.frames.columns:
            if "." in col_name:
                new_col_names.append(col_name.split(".")[1])
            else:
                new_col_names.append(col_name)

        self.frames.columns = new_col_names
