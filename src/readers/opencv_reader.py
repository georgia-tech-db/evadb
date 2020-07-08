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

from src.readers.abstract_reader import AbstractReader
from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager


class OpenCVReader(AbstractReader):

    def __init__(self, *args, **kwargs):
        """
            Reads video using OpenCV and yields frame data 
         """
        super().__init__(*args, **kwargs)

    def _read(self):
        video = cv2.VideoCapture(self.file_url)
        video_start = self.offset if self.offset else 0
        video.set(cv2.CAP_PROP_POS_FRAMES, video_start)    
        
        LoggingManager().log("Reading frames", LoggingLevel.INFO)

        _, frame = video.read()
        frame_ind = video_start - 1

        while frame is not None:
            frame_ind += 1
            yield frame
            _, frame = video.read()
