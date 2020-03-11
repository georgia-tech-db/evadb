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
from typing import Iterator

import cv2

from src.loaders.abstract_loader import AbstractVideoLoader
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.storage.frame import Frame
from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager


class VideoLoader(AbstractVideoLoader):

    def __init__(self, *args, **kwargs):
        """
            Loader which loads video frames using OpenCV.
         """
        super().__init__(*args, **kwargs)

    def _load_frames(self) -> Iterator[Frame]:
        video = cv2.VideoCapture(self.video_metadata.file_url)
        video_start = self.offset if self.offset else 0
        video.set(cv2.CAP_PROP_POS_FRAMES, video_start)

        LoggingManager().log("Loading frames", LoggingLevel.INFO)

        _, frame = video.read()
        frame_ind = video_start - 1

        info = None
        if frame is not None:
            (height, width, num_channels) = frame.shape
            info = FrameInfo(height, width, num_channels, ColorSpace.BGR)

        while frame is not None:
            frame_ind += 1
            yield Frame(frame_ind, frame, info)
            _, frame = video.read()
