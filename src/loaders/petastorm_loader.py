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
from typing import Iterator, Dict

from petastorm import make_reader

<<<<<<< HEAD:src/storage/loaders/petastorm_loader.py
from src.storage.loaders.abstract_loader import AbstractLoader
from src.models.storage.frame import Frame


class PetastormLoader(AbstractLoader):
    def __init__(self, *args, **kwargs):
        """
        Loads data frames from petastorm parquet stores.
        Internally it calls the Petastorm Reader to read frames
=======
from src.loaders.abstract_loader import AbstractVideoLoader
from src.models.storage.frame import Frame


class PetastormLoader(AbstractVideoLoader):
    def __init__(self, *args, **kwargs):
        """
        Loads parquet data frames using petastorm
>>>>>>> 3d2ed857db5f73d022da7d71c5851562c005bb09:src/loaders/petastorm_loader.py
        """
        super().__init__(*args, **kwargs)
        if self.curr_shard is not None and self.curr_shard <= 0:
            self.curr_shard = None

        if self.total_shards is not None and self.total_shards <= 0:
            self.total_shards = None

<<<<<<< HEAD:src/storage/loaders/petastorm_loader.py
    def _load_frames(self) -> Iterator[Dict]:
=======
    def _load_frames(self) -> Iterator[Frame]:
>>>>>>> 3d2ed857db5f73d022da7d71c5851562c005bb09:src/loaders/petastorm_loader.py
        with make_reader(self.video_metadata.file_url,
                         shard_count=self.total_shards,
                         cur_shard=self.curr_shard) \
                as reader:
<<<<<<< HEAD:src/storage/loaders/petastorm_loader.py
            for row in reader:
=======
            for frame_ind, row in enumerate(reader):
>>>>>>> 3d2ed857db5f73d022da7d71c5851562c005bb09:src/loaders/petastorm_loader.py
                yield row._asdict()
