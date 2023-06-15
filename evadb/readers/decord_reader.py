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

import numpy as np

from evadb.catalog.catalog_type import VideoColumnName
from evadb.constants import AUDIORATE, IFRAMES
from evadb.expression.abstract_expression import AbstractExpression
from evadb.expression.expression_utils import extract_range_list_from_predicate
from evadb.readers.abstract_reader import AbstractReader
from evadb.utils.generic_utils import try_to_import_decord
from evadb.utils.logging_manager import logger


class DecordReader(AbstractReader):
    def __init__(
        self,
        *args,
        predicate: AbstractExpression = None,
        sampling_rate: int = None,
        sampling_type: str = None,
        read_audio: bool = False,
        read_video: bool = True,
        **kwargs,
    ):
        """Read frames from the disk

        Args:
            predicate (AbstractExpression, optional): If only subset of frames
            need to be read. The predicate should be only on single column and
            can be converted to ranges. Defaults to None.
            sampling_rate (int, optional): Set if the caller wants one frame
            every `sampling_rate` number of frames. For example, if `sampling_rate = 10`, it returns every 10th frame. If both `predicate` and `sampling_rate` are specified, `sampling_rate` is given precedence.
            sampling_type (str, optional): Set as IFRAMES if caller want to sample on top on iframes only. e.g if the IFRAME frame numbers are [10,20,30,40,50] then 'SAMPLE IFRAMES 2' will return [10,30,50]
            read_audio (bool, optional): Whether to read audio stream from the video. Defaults to False
            read_video (bool, optional): Whether to read video stream from the video. Defaults to True
        """
        self._predicate = predicate
        self._sampling_rate = sampling_rate or 1
        self._sampling_type = sampling_type
        self._read_audio = read_audio
        self._read_video = read_video
        self._reader = None
        self._get_frame = None
        super().__init__(*args, **kwargs)
        self.initialize_reader()

    def _read(self) -> Iterator[Dict]:
        num_frames = int(len(self._reader))
        if self._predicate:
            range_list = extract_range_list_from_predicate(
                self._predicate, 0, num_frames - 1
            )
        else:
            range_list = [(0, num_frames - 1)]
        logger.debug("Reading frames")

        if self._sampling_type == IFRAMES:
            iframes = self._reader.get_key_indices()
            idx = 0
            for begin, end in range_list:
                while idx < len(iframes) and iframes[idx] < begin:
                    idx += self._sampling_rate

                while idx < len(iframes) and iframes[idx] <= end:
                    frame_id = iframes[idx]
                    idx += self._sampling_rate
                    yield self._get_frame(frame_id)

        elif self._sampling_rate == 1 or self._read_audio:
            for begin, end in range_list:
                frame_id = begin
                while frame_id <= end:
                    yield self._get_frame(frame_id)
                    frame_id += 1
        else:
            for begin, end in range_list:
                # align begin with sampling rate
                if begin % self._sampling_rate:
                    begin += self._sampling_rate - (begin % self._sampling_rate)
                for frame_id in range(begin, end + 1, self._sampling_rate):
                    yield self._get_frame(frame_id)

    def initialize_reader(self):
        try_to_import_decord()
        import decord

        if self._read_audio:
            assert (
                self._sampling_type != IFRAMES
            ), "Cannot use IFRAMES with audio streams"
            sample_rate = 16000
            if self._sampling_type == AUDIORATE and self._sampling_rate != 1:
                sample_rate = self._sampling_rate
            try:
                self._reader = decord.AVReader(
                    self.file_url, mono=True, sample_rate=sample_rate
                )
                self._get_frame = self.__get_audio_frame
            except decord._ffi.base.DECORDError as error_msg:
                assert "Can't find audio stream" not in str(error_msg), error_msg
        else:
            assert (
                self._sampling_type != AUDIORATE
            ), "Cannot use AUDIORATE with video streams"
            self._reader = decord.VideoReader(self.file_url)
            self._get_frame = self.__get_video_frame

    def __get_video_frame(self, frame_id):
        frame_video = self._reader[frame_id]
        frame_video = frame_video.asnumpy()
        timestamp = self._reader.get_frame_timestamp(frame_id)[0]

        return {
            VideoColumnName.id.name: frame_id,
            VideoColumnName.data.name: frame_video,
            VideoColumnName.seconds.name: round(timestamp, 2),
        }

    def __get_audio_frame(self, frame_id):
        frame_audio, _ = self._reader[frame_id]
        frame_audio = frame_audio.asnumpy()[0]

        return {
            VideoColumnName.id.name: frame_id,
            VideoColumnName.data.name: np.empty(0),
            VideoColumnName.seconds.name: 0.0,
            VideoColumnName.audio.name: frame_audio,
        }
