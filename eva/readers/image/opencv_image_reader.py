# coding=utf-8
# Copyright 2018-2022 EVA
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

from typing import Dict, Iterator

import cv2

from eva.readers.abstract_reader import AbstractReader
from eva.utils.logging_manager import logger


class CVImageReader(AbstractReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        frame = cv2.imread(str(self.file_url))
        if frame is None:
            err_msg = f"Failed to read image file {self.file_url}"
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            yield {"data": frame}
