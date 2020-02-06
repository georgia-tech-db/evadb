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
from src.udfs import video_action_classification
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame
import numpy as np
import unittest


class VidToFrameClassifier_Test(unittest.TestCase):

    def test_VidToFrameClassifier(self):
        model = video_action_classification.VideoToFrameClassifier()
        assert model is not None

        X = np.random.random([240, 320, 3])
        model.classify(FrameBatch([Frame(0, X, None)], None))
