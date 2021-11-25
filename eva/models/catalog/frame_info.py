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
from eva.models.catalog.properties import ColorSpace


class FrameInfo:
    """
    Data model contains information about the frame

    Arguments:
        height (int)(default: -1): Height of the image : left as -1
        when the height of the frame is not required

        width (int)(default: -1):  Width of the image : left as -1 when the
        height of the frame is not required

        num_channels (int)(default: 3):
        Number of input num_channels in the video

        color_space (ColorSpace)(default: ColorSpace.RGB): color space of
        the frame (RGB, HSV, BGR, GRAY)

    """

    def __init__(self, height=-1, width=-1, channels=3,
                 color_space=ColorSpace.RGB):
        self._color_space = color_space
        self._width = width
        self._height = height
        self._channels = channels

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def color_space(self):
        return self._color_space

    @property
    def num_channels(self):
        return self._channels

    def __eq__(self, other):
        return self.color_space == other.color_space and \
            self.width == other.width and \
            self.height == other.height and \
            self.num_channels == other.num_channels
