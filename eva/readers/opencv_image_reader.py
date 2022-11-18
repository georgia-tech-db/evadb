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
# from eva.utils.logging_manager import LoggingLevel
# from eva.utils.logging_manager import LoggingManager
# from eva.expression.expression_utils import parse_predicate


class CVImageReader(AbstractReader):
    def __init__(self, *args, start_frame_id=0, **kwargs):
        self._start_frame_id = start_frame_id
        self._predicate = kwargs.pop("predicate", None)
        self._resolution = kwargs.pop("resolution", None)
        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        for file in self.file_url:
            # frame = Image.open(str(file)).load()
            frame = cv2.imread(str(file))
            if frame is None:
                print("Failed to read Image {}".format(file))
            else:
                yield {"name": str(file), "data": frame}
