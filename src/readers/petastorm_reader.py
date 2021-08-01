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
from src.configuration.configuration_manager import ConfigurationManager


class PetastormReader(AbstractReader):
    def __init__(self, *args, cur_shard=None, shard_count=None,
                 predicate=None, **kwargs):
        """
        Reads data from the petastorm parquet stores. Note this won't
        work for any arbitary parquet store apart from one materialized
        using petastorm. In order to generalize, we might have to replace
        `make_reader` with `make_batch_reader`.
        https://petastorm.readthedocs.io/en/latest/api.html#module-petastorm.reader

        Attributes:
            cur_shard (int, optional): Shard number to load from if sharded
            shard_count (int, optional): Specify total number of shards if
                                      applicable
            predicate (PredicateBase, optional): instance of predicate object
                to filter rows to be returned by reader
            cache_type (str): the cache type, if desired.
            Options are [None, ‘null’, ‘local-disk’] to either have a
            null/noop cache or a cache implemented using diskcache.
            cache_location (int): the location or path of the cache.
            cache_size_limit (int): the size limit of the cache in bytes
            cache_row_size_estimate (int): the estimated size of a row
        """
        self.cur_shard = cur_shard
        self.shard_count = shard_count
        self.predicate = predicate
        petastorm_config = ConfigurationManager().get_value('storage',
                                                            'petastorm')
        # cache not allowed with predicates
        if self.predicate or petastorm_config is None:
            petastorm_config = {}
        self.cache_type = petastorm_config.get('cache_type', None)
        self.cache_location = petastorm_config.get('cache_location', None)
        self.cache_size_limit = petastorm_config.get('cache_size_limit', None)
        self.cache_row_size_estimate = petastorm_config.get(
            'cache_row_size_estimate', None)
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
                         predicate=self.predicate,
                         cache_type=self.cache_type,
                         cache_location=self.cache_location,
                         cache_size_limit=self.cache_size_limit,
                         cache_row_size_estimate=self.cache_row_size_estimate)\
                as reader:
            for row in reader:
                yield row._asdict()
