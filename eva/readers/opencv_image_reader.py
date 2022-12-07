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

from PIL import Image
import cv2
from typing import Iterator, Dict

from eva.readers.abstract_reader import AbstractReader
from eva.expression.expression_utils import extract_range_list_from_predicate


class CVImageReader(AbstractReader):
    def __init__(self, *args, start_frame_id=0, **kwargs):
        self._start_frame_id = start_frame_id
        self._predicate = kwargs.pop("predicate", None)
        self._resolution = kwargs.pop("resolution", None)
        self._num_images = kwargs.pop("num_images", 0)
        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        num_frames = self._num_images

        file_list = [str(f) for f in self.file_url]
        file_list.sort()

        if self._predicate:
            range_list = extract_range_list_from_predicate(
                self._predicate, 0, num_frames - 1
            )
        else:
            range_list = [(0, num_frames - 1)]

        for (begin, end) in range_list:
            for file_idx in range(begin, end + 1):
                
                frame = cv2.imread(file_list[file_idx])
                if frame is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    yield {"id": file_idx, "name": file_list[file_idx], "data": frame}

                
