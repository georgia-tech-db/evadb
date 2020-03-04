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
from typing import Iterator

from petastorm import make_reader

from src.loaders.abstract_loader import AbstractVideoLoader
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.storage.frame import Frame


class PetastormLoader(AbstractVideoLoader):
    def __init__(self, *args, **kwargs):
        """
        Loads parquet data frames using petastorm
        """
        super().__init__(*args, **kwargs)

    def _load_frames(self) -> Iterator[Frame]:
        info = None
        with make_reader(self.video_metadata.file,
                         shard_count=self.total_shards,
                         cur_shard=self.shard) \
                as reader:
            for frame_ind, row in enumerate(reader):
                if info is None:
                    (height, width, num_channels) = row.frame_data.shape
                    info = FrameInfo(height, width, num_channels,
                                     ColorSpace.BGR)

                yield Frame(row.frame_id, row.frame_data, info)
