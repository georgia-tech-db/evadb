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
import json
import numpy as np
import pandas as pd

from typing import List
from pandas import DataFrame
from src.utils.logging_manager import LoggingManager, LoggingLevel


class BatchEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return {"__dataframe__": obj.to_json()}
        return json.JSONEncoder.default(self, obj)


def as_batch(d):
    if "__dataframe__" in d:
        return pd.read_json(d["__dataframe__"])
    else:
        return d


class Batch:
    """
    Data model used for storing a batch of frames

    Arguments:
        frames (DataFrame): pandas Dataframe holding frames data
        identifier_column (str): A column used to uniquely a row


    """

    def __init__(self,
                 frames=pd.DataFrame(),
                 identifier_column='id'):
        super().__init__()
        # store the batch with columns sorted
        if isinstance(frames, DataFrame):
            self._frames = frames[sorted(frames.columns)]
        else:
            LoggingManager().log('Batch constructor not properly called!',
                                 LoggingLevel.DEBUG)
            raise ValueError('Batch constructor not properly called. \
                Expected pandas.DataFrame')
        self._batch_size = len(frames)
        self._identifier_column = identifier_column

    @property
    def frames(self):
        return self._frames

    @property
    def batch_size(self):
        return self._batch_size

    def __len__(self):
        return self._batch_size

    @property
    def identifier_column(self):
        return self._identifier_column

    def column_as_numpy_array(self, column_name='data'):
        return np.array(self._frames[column_name])

    def to_json(self):
        obj = {'frames': self.frames,
               'batch_size': self.batch_size,
               'identifier_column': self.identifier_column}
        return json.dumps(obj, cls=BatchEncoder)

    @classmethod
    def from_json(cls, json_str: str):
        obj = json.loads(json_str, object_hook=as_batch)
        return cls(frames=obj['frames'],
                   identifier_column=obj['identifier_column'])

    def __str__(self):
        """
        For debug propose
        """
        return 'Batch Object:\n' \
               '@dataframe: %s\n' \
               '@batch_size: %d\n' \
               '@identifier_column: %s' \
               % (self._frames, self._batch_size, self.identifier_column)

    def __eq__(self, other: 'Batch'):
        return self.frames.equals(other.frames)

    def _get_frames_from_indices(self, required_frame_ids):
        new_frames = self.frames.iloc[required_frame_ids, :]
        new_batch = Batch(new_frames)
        return new_batch

    def __getitem__(self, indices) -> 'Batch':
        """
        Takes as input the slice for the list
        Arguments:
            item (list or Slice):

        :return:
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

    def sort(self, by=None):
        """
        in_place sort
        """
        if by is None and self.identifier_column in self._frames:
            by = [self.identifier_column]
        self._frames.sort_values(by=by, ignore_index=True, inplace=True)

    def sort_orderby(self, by, sort_type):
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
                    LoggingManager().log(
                        'Can not orderby non-projected column: {}'.format(
                            column),
                        LoggingLevel.ERROR)
                    raise KeyError(
                        'Can not orderby non-projected column: {}'.format(
                            column))

            self._frames.sort_values(
                by, ascending=sort_type, ignore_index=True, inplace=True)
        else:
            LoggingManager().log(
                'Columns and Sort Type are required for orderby',
                LoggingLevel.WARNING)

    def project(self, cols: []) -> 'Batch':
        """
        Takes as input the column list, returns the projection.
        We do a copy for now.
        """
        verfied_cols = [c for c in cols if c in self._frames]
        unknown_cols = list(set(cols) - set(verfied_cols))
        if len(unknown_cols):
            LoggingManager().log("Unexpected columns %s\n\
                                 Frames: %s" % (unknown_cols, self._frames),
                                 LoggingLevel.WARNING)
        return Batch(self._frames[verfied_cols], self._identifier_column)

    @classmethod
    def merge_column_wise(cls,
                          batches: ['Batch'],
                          auto_renaming=False) -> 'Batch':
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
            LoggingManager().log(
                'Duplicated column name detected {}'.format(new_frames),
                LoggingLevel.WARNING)
        return Batch(new_frames)

    def __add__(self, other: 'Batch'):
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
    def concat(cls, batch_list: List['Batch'], copy=True) -> 'Batch':
        """ Concat a list of batches. Avoid the extra copying overhead by
        the append operation in __add__.
        Notice: only frames are considered.
        """

        frame_list = [batch.frames for batch in batch_list]
        frame = pd.concat(frame_list, ignore_index=True, copy=copy)

        return Batch(frame)

    def empty(self):
        """Checks if the batch is empty
        Returns:
            True if the batch_size == 0
        """
        return self.batch_size == 0

    def reverse(self):
        """ Reverses dataframe """
        self._frames = self._frames[::-1]
        self._frames.reset_index(drop=True, inplace=True)

    def reset_index(self):
        """ Resets the index of the data frame in the batch"""
        self._frames.reset_index(drop=True, inplace=True)
