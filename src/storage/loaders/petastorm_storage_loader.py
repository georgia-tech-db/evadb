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

from src.storage.loaders.abstract_storage_loader import AbstractStorageLoader
from src.models.storage.frame import Frame

from src.readers.petastorm_reader import PetastormReader


class PetastormStorageLoader(AbstractStorageLoader):
    def __init__(self, *args, **kwargs):
        """
        Loads data frames from petastorm parquet stores.
        Internally it calls the Petastorm Reader to read frames
        """
        super().__init__(*args, **kwargs)
        if self.curr_shard is not None and self.curr_shard <= 0:
            self.curr_shard = None

        if self.total_shards is not None and self.total_shards <= 0:
            self.total_shards = None

    def _load_frames(self) -> Iterator[Frame]:
        reader = PetastormReader(self.video_metadata.file_url,
                                 shard_count=self.total_shards,
                                 cur_shard=self.curr_shard)
        for row in reader.read():
            yield row
