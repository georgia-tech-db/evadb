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
from typing import Dict, Iterator

import librosa

from eva.readers.abstract_reader import AbstractReader
from eva.utils.generic_utils import extract_audio


class AudioReader(AbstractReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        audio_file = extract_audio(self.file_url)
        audio_array, sr = librosa.load(audio_file, sr=16_000)

        # create segments of 30 seconds
        segment_length = 30
        # number of samples in each segment
        segment_samples = int(segment_length * sr)

        for i in range(0, len(audio_array), segment_samples):
            segment = audio_array[i : i + segment_samples]
            yield {"data": segment}
