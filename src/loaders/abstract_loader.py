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
from typing import Iterator, Dict

import pandas as pd

from src.catalog.models.df_metadata import DataFrameMetadata
from src.models.storage.batch import Batch


class AbstractVideoLoader(metaclass=ABCMeta):
    """
    Abstract class for defining video loader. All other video loaders use this
    abstract class. Video loader are expected fetch the videos from storage
    and return the frames in an iterative manner.

    Attributes:
        video_metadata (DataFrameMetadata): Object containing metadata of video
        batch_size (int, optional): No. of frames to fetch in batch from video
        skip_frames (int, optional): Number of frames to be skipped
                                     while fetching the video
        offset (int, optional): Start frame location in video
        limit (int, optional): Number of frames needed from the video
        curr_shard (int, optional): Shard number to load from if sharded
        total_shards (int, optional): Specify total number of shards if
                                      applicable
    """

    def __init__(self, video_metadata: DataFrameMetadata, batch_size=1,
                 skip_frames=0, offset=None, limit=None, curr_shard=0,
                 total_shards=0):
        self.video_metadata = video_metadata
        self.batch_size = batch_size
        self.skip_frames = skip_frames
        self.offset = offset
        self.limit = limit
        self.curr_shard = curr_shard
        self.total_shards = total_shards
        self.identifier_column = video_metadata.identifier_column if video_metadata.identifier_column else 'id'

    def load(self) -> Iterator[Batch]:
        """
        This is a generator for loading the frames of a video.
         Uses the video metadata and other class arguments

        Yields:
        :obj: `Batch`: An object containing a batch of frames
                                       and record specific metadata
        """

        frames = []
        for record in self._load_frames():
            if self.skip_frames > 0 and record.get(self.identifier_column,
                                                   0) % self.skip_frames != 0:
                continue
            if self.limit and record.get(self.identifier_column,
                                         0) >= self.limit:
                return Batch(pd.DataFrame(frames),
                             identifier_column=self.identifier_column)
            frames.append(record)
            if len(frames) % self.batch_size == 0:
                yield Batch(pd.DataFrame(frames),
                            identifier_column=self.identifier_column)
                frames = []
        if frames:
            return Batch(pd.DataFrame(frames),
                         identifier_column=self.identifier_column)

    @abstractmethod
    def _load_frames(self) -> Iterator[Dict]:
        """
        Loads video frames from storage and returns the Frame type.

        Yields:
            Frame:  A frame object of the video, used for processing.
        """
