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
from src.models.catalog.properties import VideoFormat


class VideoMetaInfo:
    """
    Data model used for storing video related information
    # TODO: This is database metadata. Need to discuss what goes in here

    Arguments:
        file (str): path where the video is stored
        fps (int): Frames per second in the video
        c_format (VideoFormat): Video File Format

    """

    def __init__(self, file: str, fps: int, c_format: VideoFormat):
        self._fps = fps
        self._file = file
        self._c_format = c_format

    @property
    def file(self) -> str:
        return self._file

    @property
    def fps(self) -> int:
        return self._fps

    @property
    def c_format(self) -> VideoFormat:
        return self._c_format
