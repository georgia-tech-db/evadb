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
import unittest

import numpy as np

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.storage.frame import Frame

from src.loaders.frame_loader import FrameLoader

NUM_FRAMES = 10


class FrameLoaderTest(unittest.TestCase):

    def create_dummy_frames(self, num_frames=NUM_FRAMES, filters=[]):
        if not filters:
            filters = range(num_frames)
        for i in filters:
            yield Frame(i,
                        np.array(np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                                 dtype=np.uint8),
                        FrameInfo(2, 2, 3, ColorSpace.BGR))

    def setUp(self):
        self.create_dummy_frames(NUM_FRAMES)

    def test_frameinfo_information(self):

        frame_info = FrameInfo(2, 2, 3, ColorSpace.BGR)
        f = FrameLoader("appname", frame_info)

        self.assertEqual(f.H, 2)
