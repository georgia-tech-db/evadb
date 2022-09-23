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
from abc import ABCMeta
from typing import List

import pandas as pd
from numpy.typing import ArrayLike

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace


class UDF:
    """
    Class for all UDFs.

    TODO: We might need to store the labels somewhere
    """

    def __init__(self):
        pass

    @property
    def name(self) -> stt

    def setup(
        self,
        setup_func=None,
        cache=True,
        requirements=["tqdm"],
        model_path=["path/to/model"],
    ):
        # TODO: perform the basic setup instructions here
        pass

    def preprocess(
        self,
        preprocess_func=None,
        input_type=PILImage,
        input_frame_shape=(3, 1, -1),
        batch=True
    ):
        # TODO: perform the basic preprocess instructions here
        pass

    def forward(
        self,
        forward_func=None,
        input_type=TorchTensor,
        input_frame_shape=(3,1,-1),
        output_type=PdDataFrame
    ):
        # TODO: perform the basic forward instructions here
        pass
