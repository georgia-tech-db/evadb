import pickle
import shutil
from typing import Any
from diskcache import FanoutCache


class DiskKVCache:
    """Disk key value cache

    Args:
        `path` (str): the path on disk where the cache will be stored
        `max_cache_size` (int, optional): an integer representing the maximum size of
            the cache. The system will make its best effort to enforce this limit, but it may slightly exceed it. The default value is 2**30.
        `shards` (int, optional): an integer representing the number of shards to use.
            This can improve concurrent writes. The default value is 6.
    """

    def __init__(self, path: str, max_cache_size: int = 2**30, shards: int = 6):
        # For details, see: http://www.grantjenks.com/docs/diskcache/tutorial.html#settings
        default_settings = {
            "size_limit": max_cache_size,
            "eviction_policy": "least-recently-stored",
            "disk_pickle_protocol": pickle.HIGHEST_PROTOCOL,
        }
        self._path = path
        self._cache = FanoutCache(path, shards=shards, settings=default_settings)

    def get(self, key: Any):
        value = self._cache.get(key, default=None)
        return value

    def set(self, key: Any, value: Any):
        self._cache.set(key, value)

    def cleanup(self):
        shutil.rmtree(self._path)
