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
from petastorm import make_reader
from typing import Iterator, Dict

from src.readers.abstract_reader import AbstractReader


class PetastormReader(AbstractReader):
    def __init__(self, *args, cur_shard=None, shard_count=None,
                 predicate=None, **kwargs):
        """
        Reads data from the petastorm parquet stores. Note this won't
        work for any arbitary parquet store apart from one materialized
        using petastorm. In order to generalize, we might have to replace
        `make_reader` with `make_batch_reader`.
        Attributes:
            cur_shard (int, optional): Shard number to load from if sharded
            shard_count (int, optional): Specify total number of shards if
                                      applicable
            predicate (PredicateBase, optional): instance of predicate object
                to filter rows to be returned by reader

        """
        self.cur_shard = cur_shard
        self.shard_count = shard_count
        self.predicate = predicate
        super().__init__(*args, **kwargs)
        if self.cur_shard is not None and self.cur_shard <= 0:
            self.cur_shard = None

        if self.shard_count is not None and self.shard_count <= 0:
            self.shard_count = None

    def _read(self) -> Iterator[Dict]:
        # `Todo`: Generalize this reader
        with make_reader(self.file_url,
                         shard_count=self.shard_count,
                         cur_shard=self.cur_shard,
                         predicate=self.predicate) \
                as reader:
            for row in reader:
                yield row._asdict()
