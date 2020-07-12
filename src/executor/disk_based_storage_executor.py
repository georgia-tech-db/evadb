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

from src.readers.opencv_reader import OpenCVReader
from src.models.storage.batch import Batch
from src.executor.abstract_storage_executor import \
    AbstractStorageExecutor
from src.planner.storage_plan import StoragePlan


class DiskStorageExecutor(AbstractStorageExecutor):
    """
    This is a simple disk based executor. It assumes that frames are
    directly being read from the disk(video file).

    Note: For a full fledged deployment this might be replaced with a
    Transaction manager which keeps track of the frames.
    """

    def __init__(self, node: StoragePlan):
        super().__init__(node)
        """
        self.storage = Loader(node.video,
                              batch_size=node.batch_size,
                              skip_frames=node.skip_frames,
                              limit=node.limit,
                              offset=node.offset,
                              curr_shard=node.curr_shard,
                              total_shards=node.total_shards)
        """
        self.storage = OpenCVReader(node.video,
                                    batch_size=node.batch_size,
                                    offset=node.offset)

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        for batch in self.storage.read():
            yield batch
