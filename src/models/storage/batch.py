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
from typing import List

import numpy as np


class FrameBatch:
    """
    Data model used for storing a batch of frames

    Arguments:
        frames (List[Frame]): List of video frames
        info (FrameInfo): Information about the frames in the batch
        outcomes (Dict[str, List[BasePrediction]]): outcomes of running a udf
        with name 'x' as key


    """

    def __init__(self, frames, info, outcomes=None, temp_outcomes=None):
        super().__init__()
        if outcomes is None:
            outcomes = dict()
        if temp_outcomes is None:
            temp_outcomes = dict()

        self._info = info
        self._frames = tuple(frames)
        self._batch_size = len(frames)
        self._outcomes = outcomes
        self._temp_outcomes = temp_outcomes

    @property
    def frames(self):
        return self._frames

    @property
    def info(self):
        return self._info

    @property
    def batch_size(self):
        return self._batch_size

    def frames_as_numpy_array(self):
        return np.array([frame.data for frame in self.frames])

    def __eq__(self, other: 'FrameBatch'):
        return self.info == other.info and \
            self.frames == other.frames and \
            self._outcomes == other._outcomes and \
            self._temp_outcomes == other._temp_outcomes

    def set_outcomes(self, name, predictions: 'BasePrediction',
                     is_temp: bool = False):
        """
        Used for storing outcomes of the UDF predictions

        Arguments:
            name (str): name of the UDF to which the predictions belong to

            predictions (BasePrediction): Predictions/Outcome after executing
            the UDF on prediction

            is_temp (bool, default: False): Check if the outcomes are temporary

        """
        if is_temp:
            self._temp_outcomes[name] = predictions
        else:
            self._outcomes[name] = predictions

    def get_outcomes_for(self, name: str) -> List['BasePrediction']:
        """
        Returns names corresponding to a name
        Arguments:
            name (str): name of the udf on which predicate is being executed

        Returns:
            List[BasePrediction]
        """
        if name in self._outcomes:
            return self._outcomes.get(name, [])
        else:
            return self._temp_outcomes.get(name, [])

    def has_outcome(self, name: str):
        """
        Method used for checking if the outcome with given name is present.
        Either in temporary outcomes or actual outcomes.

        Arguments:
            name (str): name of the outcome to check
        Returns:
            bool: True if present else false
        """

        return name in self._outcomes or name in self._temp_outcomes

    def _get_frames_from_indices(self, required_frame_ids):
        new_frames = [self.frames[i] for i in required_frame_ids]
        new_batch = FrameBatch(new_frames, self.info)
        for key in self._outcomes:
            new_batch._outcomes[key] = [self._outcomes[key][i]
                                        for i in required_frame_ids]
        for key in self._temp_outcomes:
            new_batch._temp_outcomes[key] = [self._temp_outcomes[key][i]
                                             for i in required_frame_ids]
        return new_batch

    def __getitem__(self, indices) -> 'FrameBatch':
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
