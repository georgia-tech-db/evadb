# coding=utf-8
# Copyright 2019 EVA
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

from enum import Enum


class ColorSpace(Enum):
    RGB = 1
    HSV = 2
    BGR = 3
    GRAY = 4


class VideoFormat(Enum):
    MOV = 1
    WMV = 2
    OGG = 3
    AVI = 4
    FLV = 5
    MP4 = 6
    MPEG = 7
