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
import unittest

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace


class FrameInfoTest(unittest.TestCase):
    def test_frame_info_equality(self):
        info1 = FrameInfo(
            height=250, width=250, channels=3, color_space=ColorSpace.GRAY
        )
        info2 = FrameInfo(250, 250, 3, color_space=ColorSpace.GRAY)
        self.assertEqual(info1, info2)
