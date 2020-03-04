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

from src.models.catalog.video_info import VideoMetaInfo
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame


class AbstractVideoLoader(metaclass=ABCMeta):
    """
    Abstract class for defining video loader. All other video loaders use this
    abstract class. Video loader are expected fetch the videos from storage
    and return the frames in an iterative manner.

    Attributes:
        video_metadata (VideoMetaInfo): Object containing metadata of the video
        batch_size (int, optional): No. of frames to fetch in batch from video
        skip_frames (int, optional): Number of frames to be skipped
                                     while fetching the video
        offset (int, optional): Start frame location in video
        limit (int, optional): Number of frames needed from the video
        shard (int, optional): Shard number to load from if sharded
        total_shards (int, optional): Specify total number of shards if
                                      applicable
    """

    def __init__(self, video_metadata: VideoMetaInfo, batch_size=1,
                 skip_frames=0, offset=None, limit=None, shard=0,
                 total_shards=0):
        self.video_metadata = video_metadata
        self.batch_size = batch_size
        self.skip_frames = skip_frames
        self.offset = offset
        self.limit = limit
        self.shard = shard
        self.total_shards = total_shards

    def load(self) -> Iterator[FrameBatch]:
        """
        This is a generator for loading the frames of a video.
         Uses the video metadata and other class arguments

        Yields:
        :obj: `eva.models.FrameBatch`: An object containing a batch of frames
                                       and frame specific metadata
        """

        frames = []
        for frame in self._load_frames():
            if self.skip_frames > 0 and frame.index % self.skip_frames != 0:
                continue
            if self.limit and frame.index >= self.limit:
                return FrameBatch(frames, frame.info)
            frames.append(frame)
            if len(frames) % self.batch_size == 0:
                yield FrameBatch(frames, frame.info)
                frames = []
        if frames:
            return FrameBatch(frames, frames[0].info)

    @abstractmethod
    def _load_frames(self) -> Iterator[Frame]:
        """
        Loads video frames from storage and returns the Frame type.

        Yields:
            Frame:  A frame object of the video, used for processing.
        """
