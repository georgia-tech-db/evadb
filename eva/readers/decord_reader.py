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
import math
from typing import Dict, Iterator

import numpy as np

from eva.constants import IFRAMES
from eva.expression.abstract_expression import AbstractExpression
from eva.expression.expression_utils import extract_range_list_from_predicate
from eva.readers.abstract_reader import AbstractReader
from eva.utils.logging_manager import logger

# Lazy import to avoid torch init failures
_decord = None


def _lazy_import_decord():
    global _decord
    if _decord is None:
        import decord

        _decord = decord
    return _decord


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
            sampling_type (str, optional): Set as IFRAMES if caller want to sample on top on iframes only. e.g if the IFRAME frame numbers are [10,20,30,40,50] then'SAMPLE IFRAMES 2' will return [10,30,50]
            read_audio (bool, optional): Whether to read audio stream from the video. Defaults to False
            read_video (bool, optional): Whether to read video stream from the video. Defaults to True
        """
        self._predicate = predicate
        self._sampling_rate = sampling_rate or 1
        self._sampling_type = sampling_type
        self._read_audio = read_audio
        self._read_video = read_video
        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        decord = _lazy_import_decord()
        has_audio = False
        # Check for availability of audio stream
        # If there is an audio stream => AVReader
        # Else => VideoReader (no audio)
        if self._read_audio:
            try:
                av_reader = decord.AVReader(self.file_url, mono=True, sample_rate=16000)
                has_audio = True
            except decord._ffi.base.DECORDError as error_msg:
                if "Can't find audio stream" in str(error_msg):
                    print("No audio stream in video")

        v_reader = decord.VideoReader(self.file_url)

        num_frames = int(len(v_reader))
        if self._predicate:
            range_list = extract_range_list_from_predicate(
                self._predicate, 0, num_frames - 1
            )
        else:
            range_list = [(0, num_frames - 1)]
        logger.debug("Reading frames")

        if self._sampling_type == IFRAMES:
            iframes = v_reader.get_key_indices()
            idx = 0
            for begin, end in range_list:
                while idx < len(iframes) and iframes[idx] < begin:
                    idx += self._sampling_rate

                while idx < len(iframes) and iframes[idx] <= end:
                    frame_id = iframes[idx]
                    if has_audio:
                        frame_audio, frame = av_reader[frame_id]
                        frame_audio = frame_audio.asnumpy()
                        if self._read_video is None or not self._read_video:
                            frame = np.empty(0)
                    else:
                        frame = v_reader[frame_id]
                        frame_audio = np.empty(0)
                    frame = frame.asnumpy()
                    timestamp = v_reader.get_frame_timestamp(frame_id)[0]
                    idx += self._sampling_rate
                    if frame is not None:
                        yield {
                            "id": frame_id,
                            "data": frame,
                            "seconds": math.floor(timestamp),
                            "audio": frame_audio,
                        }
                    else:
                        break
        elif self._sampling_rate == 1:
            for begin, end in range_list:
                frame_id = begin
                while frame_id <= end:
                    if has_audio:
                        frame_audio, frame = av_reader[frame_id]
                        frame_audio = frame_audio.asnumpy()
                        if self._read_video is None or not self._read_video:
                            frame = np.empty(0)
                    else:
                        frame = v_reader[frame_id]
                        frame_audio = np.empty(0)
                    frame = frame.asnumpy()
                    timestamp = v_reader.get_frame_timestamp(frame_id)[0]
                    if frame is not None:
                        yield {
                            "id": frame_id,
                            "data": frame,
                            "seconds": math.floor(timestamp),
                            "audio": frame_audio,
                        }
                    else:
                        break
                    frame_id += 1
        else:
            for begin, end in range_list:
                # align begin with sampling rate
                if begin % self._sampling_rate:
                    begin += self._sampling_rate - (begin % self._sampling_rate)
                for frame_id in range(begin, end + 1, self._sampling_rate):
                    if has_audio:
                        frame_audio, frame = av_reader[frame_id]
                        frame_audio = frame_audio.asnumpy()
                        if self._read_video is None or not self._read_video:
                            frame = np.empty(0)
                    else:
                        frame = v_reader[frame_id]
                        frame_audio = np.empty(0)
                    frame = frame.asnumpy()
                    timestamp = v_reader.get_frame_timestamp(frame_id)[0]
                    if frame is not None:
                        yield {
                            "id": frame_id,
                            "data": frame,
                            "seconds": math.floor(timestamp),
                            "audio": frame_audio,
                        }
                    else:
                        break
