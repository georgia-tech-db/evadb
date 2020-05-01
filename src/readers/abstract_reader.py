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
from abc import ABCMeta, abstractmethod
from typing import Iterator

from src.catalog.models.df_metadata import DataFrameMetadata
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame


class AbstractReader(metaclass=ABCMeta):
    """
    Abstract class for defining data reader. All other video readers use this
    abstract class. Video readers are expected to read data and return the frames in an iterative manner.

    Attributes:
        file_path (str): path to read data from
        batch_size (int, optional): No. of frames to read in batch from video
        offset (int, optional): Start frame location in video
        """

    def __init__(self, file_path: str, batch_size=1,
                 offset=None):
        self.file_path = file_path
        self.batch_size = batch_size
        self.offset = offset
        
    def load(self) -> Iterator[FrameBatch]:
        """
        This is a generator for loading the frames of a video.
         Uses the video metadata and other class arguments

        Yields:
        :obj: `Batch`: An object containing a batch of frames
                                       and frame specific metadata
        """

        frames = []
        for frame in self._read():
            frames.append(frame)
            if len(frames) % self.batch_size == 0:
                yield FrameBatch(frames, frame.info)
                frames = []
        if frames:
            return FrameBatch(frames, frames[0].info)

    @abstractmethod
    def _read(self) -> Iterator[Frame]:
        """
        reads data and returns the frame object.

        Yields:
            Frame:  A frame object of the video, used for processing.
        """
