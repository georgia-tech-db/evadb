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
import numpy as np


class Frame:
    """
    Data model used for storing video frame related information

    Arguments:
        id (int): The index of the frame in video(Frame number)
        data (numpy.ndarray): Frame object from video
        info (FrameInfo): Contains properties of the frame

    """

    def __init__(self, id, data, info):
        self._data = data
        self._id = id
        self._info = info

    @property
    def data(self):
        return self._data

    @property
    def id(self):
        return self._id

    @property
    def info(self):
        return self._info

    def __eq__(self, other):
        return self.index == other.index and \
            np.array_equal(self.data, other.data) and \
            self.info == other.info

    def asdict(self):
        return {'id': self._id, 'data': self._data, 'info': self._info}
