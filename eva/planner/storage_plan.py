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
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.expression.abstract_expression import AbstractExpression
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class StoragePlan(AbstractPlan):
    """
    This is the plan used for retrieving the frames from the storage and
    and returning to the higher levels.

    Arguments:
        video (DataFrameMetadata): Required meta-data for fetching data
        batch_mem_size (int): memory size of the batch read from disk
        skip_frames (int): skip frequency
        offset (int): storage offset for retrieving data
        limit (int): limit on data records to be retrieved
        total_shards (int): number of shards of data (if sharded)
        curr_shard (int): current curr_shard if data is sharded
        sampling_rate (int): uniform sampling rate
    """

    def __init__(
        self,
        video: DataFrameMetadata,
        batch_mem_size: int,
        skip_frames: int = 0,
        offset: int = None,
        limit: int = None,
        total_shards: int = 0,
        curr_shard: int = 0,
        predicate: AbstractExpression = None,
        sampling_rate: int = None,
    ):
        super().__init__(PlanOprType.STORAGE_PLAN)
        self._video = video
        self._batch_mem_size = batch_mem_size
        self._skip_frames = skip_frames
        self._offset = offset
        self._limit = limit
        self._total_shards = total_shards
        self._curr_shard = curr_shard
        self._predicate = predicate
        self._sampling_rate = sampling_rate

    @property
    def video(self):
        return self._video

    @property
    def batch_mem_size(self):
        return self._batch_mem_size

    @property
    def skip_frames(self):
        return self._skip_frames

    @property
    def offset(self):
        return self._offset

    @property
    def limit(self):
        return self._limit

    @property
    def total_shards(self):
        return self._total_shards

    @property
    def curr_shard(self):
        return self._curr_shard

    @property
    def predicate(self):
        return self._predicate

    @property
    def sampling_rate(self):
        return self._sampling_rate

    def __str__(self):
        return "StoragePlan(video={}, \
            batch_mem_size={}, \
            skip_frames={}, \
            offset={}, \
            limit={}, \
            total_shards={}, \
            curr_shard={}, \
            predicate={}, \
            sampling_rate={})".format(
            self._video,
            self._batch_mem_size,
            self._skip_frames,
            self._offset,
            self._limit,
            self._total_shards,
            self._curr_shard,
            self._predicate,
            self._sampling_rate,
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.video,
                self.batch_mem_size,
                self.skip_frames,
                self.offset,
                self.limit,
                self.total_shards,
                self.curr_shard,
                self.predicate,
                self.sampling_rate,
            )
        )
