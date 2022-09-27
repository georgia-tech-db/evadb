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
from turtle import forward
from typing import List

import pandas as pd
from numpy.typing import ArrayLike

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace

from typing import List

import numpy as np
import pandas as pd
import torch
from numpy.typing import ArrayLike
from PIL import Image
from torch import Tensor, nn
from torchvision.transforms import Compose, transforms

class UDF:
    def setup_decorator(name=None,cache=True):
        def Inner(func):
            def wrapper(self):
                self.name = name
                self.transform = [transforms.ToTensor()]
                return func(self)
            return wrapper
        return Inner

    def preprocess_decorator():
        def Inner(func):
            def wrapper(self):
                return func(self)
            return wrapper
        return Inner

    def forward_decorator():
        def Inner(func):
            def wrapper(self, frames):
                return func(self, frames)
            return wrapper
        return Inner
