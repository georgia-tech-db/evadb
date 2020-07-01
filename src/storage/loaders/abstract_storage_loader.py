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
from src.models.storage.batch import Batch
from src.models.storage.frame import Frame


class AbstractStorageLoader(metaclass=ABCMeta):
    """
    Abstract class for defining storage loader. All other loaders use this
    abstract class. Video loaders are expected to fetch videos from the storage
    and return the frames in an iterative manner.
    Right now we internally store videos in petastorm parquet stores.
    But moving forward we will add support for other parquet stores.


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

    def load(self) -> Iterator[Batch]:
        """
        This is a generator for loading the frames of a video.
         Uses the video metadata and other class arguments

        Yields:
        FrameBatch: An object containing a batch of frames
                                       and frame specific metadata
        """

        frames = []
        for frame in self._load_frames():
            if self.skip_frames > 0 and frame.index % self.skip_frames != 0:
                continue
            if self.limit and frame.index >= self.limit:
                return Batch(frames)
            frames.append(frame)
            if len(frames) % self.batch_size == 0:
                yield Batch(frames)
                frames = []
        if frames:
            return Batch(frames)

    @abstractmethod
    def _load_frames(self) -> Iterator[Frame]:
        """
        Loads video frames from storage and returns the Frame type.

        Yields:
            Frame:  A frame object of the video, used for processing.
        """
