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

from torch import Tensor
from torch import nn
from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.pytorch_abstract_udf import PytorchAbstractFilterUDF

class BoxBlur(PytorchAbstractFilterUDF):
    """
    A pytorch based classifier. Used to make sure we make maximum
    utilization of features provided by pytorch without reinventing the wheel.
    """

    @property
    def name(self) -> str:
        return "boxblur"

    def __init__(self,
                 kernel_size=3,
                 stride=1,
                 padding=0,
                 padding_mode='zeros',
                 dilation=1):

        self.ksize = kernel_size
        self.stride = stride
        self.padding = padding
        self.padding_mode = padding_mode

    @property
    def input_format(self) -> FrameInfo:
        # TODO: figure this out
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    def _get_frames(self, frames: Tensor) -> Tensor:
        pass
