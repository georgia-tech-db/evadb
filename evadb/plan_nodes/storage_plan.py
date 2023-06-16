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
from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.expression.abstract_expression import AbstractExpression
from evadb.parser.table_ref import TableRef
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType


class StoragePlan(AbstractPlan):
    """
    This is the plan used for retrieving the frames from the storage and
    and returning to the higher levels.

    Arguments:
        table (TableCatalogEntry): table for fetching data
        batch_mem_size (int): memory size of the batch read from disk
        skip_frames (int): skip frequency
        offset (int): storage offset for retrieving data
        limit (int): limit on data records to be retrieved
        total_shards (int): number of shards of data (if sharded)
        curr_shard (int): current curr_shard if data is sharded
        sampling_rate (int): uniform sampling rate
        sampling_type (str): special sampling type like IFRAMES
    """

    def __init__(
        self,
        table: TableCatalogEntry,
        table_ref: TableRef,
        skip_frames: int = 0,
        offset: int = None,
        limit: int = None,
        total_shards: int = 0,
        curr_shard: int = 0,
        predicate: AbstractExpression = None,
        sampling_rate: int = None,
        batch_mem_size: int = 30000000,
        sampling_type: str = None,
        chunk_params: dict = {},
    ):
        super().__init__(PlanOprType.STORAGE_PLAN)
        self._table = table
        self._table_ref = table_ref
        self._batch_mem_size = batch_mem_size
        self._skip_frames = skip_frames
        self._offset = offset
        self._limit = limit
        self._total_shards = total_shards
        self._curr_shard = curr_shard
        self._predicate = predicate
        self._sampling_rate = sampling_rate
        self._sampling_type = sampling_type
        self.chunk_params = chunk_params

    @property
    def table(self):
        return self._table

    @property
    def table_ref(self):
        return self._table_ref

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

    @property
    def sampling_type(self):
        return self._sampling_type

    def __str__(self):
        return "StoragePlan(video={}, \
            table_ref={},\
            batch_mem_size={}, \
            skip_frames={}, \
            offset={}, \
            limit={}, \
            total_shards={}, \
            curr_shard={}, \
            predicate={}, \
            sampling_rate={}, \
            sampling_type={})".format(
            self._table,
            self._table_ref,
            self._batch_mem_size,
            self._skip_frames,
            self._offset,
            self._limit,
            self._total_shards,
            self._curr_shard,
            self._predicate,
            self._sampling_rate,
            self._sampling_type,
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table,
                self.table_ref,
                self.batch_mem_size,
                self.skip_frames,
                self.offset,
                self.limit,
                self.total_shards,
                self.curr_shard,
                self.predicate,
                self.sampling_rate,
                self.sampling_type,
                frozenset(self.chunk_params.items()),
            )
        )
