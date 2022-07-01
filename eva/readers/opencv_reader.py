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
from typing import Iterator, Dict

from eva.readers.abstract_reader import AbstractReader
from eva.utils.logging_manager import logger

class OpenCVReader(AbstractReader):

    def __init__(self, *args, start_frame_id=0, **kwargs):
        """
            Reads video using OpenCV and yields frame data.
            It will use the `start_frame_id` while annotating the
            frames. The first frame will be annotated with `start_frame_id`
            Attributes:
                start_frame_id (int): id assigned to first read frame
                    eg: start_frame_id=10, returned Iterator will be
                    [{10, frame1}, {11, frame2} ...]
                    It is different from offset. Offset defines where in video
                    should we start reading. And start_frame_id defines the id
                    we assign to first read frame.
         """
        self._start_frame_id = start_frame_id
        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        video = cv2.VideoCapture(self.file_url)
        video_offset = self.offset if self.offset else 0
        video.set(cv2.CAP_PROP_POS_FRAMES, video_offset)

        logger.debug("Reading frames")

        _, frame = video.read()
        frame_id = self._start_frame_id

        while frame is not None:
            yield {'id': frame_id, 'data': frame}
            _, frame = video.read()
            frame_id += 1
