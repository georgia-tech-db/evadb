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
import pickle
from typing import Any

from diskcache import FanoutCache


class DiskKVCache:
    """Disk key value cache

    Args:
        `path` (str): the path on disk where the cache will be stored
        `max_cache_size` (int, optional): an integer representing the maximum size of
            the cache. The system will make its best effort to enforce this limit, but it may slightly exceed it. The default value is 2**30.
        `shards` (int, optional): an integer representing the number of shards to use.
            This can improve concurrent writes. The default value is 3. size limit of
            individual cache shards is the `max_cache_size` divided by the number of
            shards.
    """

    def __init__(self, path: str, max_cache_size: int = 2**30, shards: int = 3):
        # For details, see: http://www.grantjenks.com/docs/diskcache/tutorial.html#settings
        default_settings = {
            "size_limit": max_cache_size,
            "eviction_policy": "least-recently-stored",
            "disk_pickle_protocol": pickle.HIGHEST_PROTOCOL,
        }
        self._path = path
        self._cache = FanoutCache(path, shards=shards, **default_settings)

    def get(self, key: Any):
        value = self._cache.get(key, default=None)
        return value

    def set(self, key: Any, value: Any):
        self._cache.set(key, value)
