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
import cv2

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.catalog.video_info import VideoMetaInfo
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame

from src.utils.logging import Logger
from src.utils.logging import LoggingLevel


class VideoLoader():
    def __init__(self, video_metadata: VideoMetaInfo, batch_size=1,
                 skip_frames=0, offset=None, limit=None):
        """
         Abstract class for defining video loader.
         All other video loaders use this abstract class.
         Video loader are expected fetch the videos from storage
         and return the frames in an iterative manner.

         Attributes:
             video_metadata (VideoMetaInfo):
             Object containing metadata of the video
             batch_size (int, optional):
            No. of frames to fetch in batch from video
             skip_frames (int, optional):
             Number of frames to be skipped while fetching the video
             offset (int, optional): Start frame location in video
             limit (int, optional): Number of frames needed from the video
         """
        self.video_metadata = video_metadata
        self.batch_size = batch_size
        self.skip_frames = skip_frames
        self.offset = offset
        self.limit = limit

    def load(self):
        video = cv2.VideoCapture(self.video_metadata.file)
        video_start = self.offset if self.offset else 0
        video.set(cv2.CAP_PROP_POS_FRAMES, video_start)

        Logger().log("Loading frames", LoggingLevel.CRITICAL)

        _, frame = video.read()
        frame_ind = video_start - 1

        info = None
        if frame is not None:
            (height, width, num_channels) = frame.shape
            info = FrameInfo(height, width, num_channels, ColorSpace.BGR)

        frames = []
        while frame is not None:
            frame_ind += 1
            eva_frame = Frame(frame_ind, frame, info)
            if self.skip_frames > 0 and frame_ind % self.skip_frames != 0:
                _, frame = video.read()
                continue

            frames.append(eva_frame)
            if self.limit and frame_ind >= self.limit:
                return FrameBatch(frames, info)

            if len(frames) % self.batch_size == 0:
                yield FrameBatch(frames, info)
                frames = []

            _, frame = video.read()

        if frames:
            return FrameBatch(frames, info)
