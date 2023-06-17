# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.readers.abstract_reader import AbstractReader
from evadb.utils.generic_utils import try_to_import_cv2


class CVImageReader(AbstractReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        try_to_import_cv2()
        import cv2

        im_bgr = cv2.imread(str(self.file_url))
        im_rgb = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2RGB)
        assert im_rgb is not None, f"Failed to read image file {self.file_url}"
        yield {"data": im_rgb}
