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
import itertools
from typing import Iterator

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.rebatch_plan import RebatchPlan
from evadb.utils.generic_utils import get_size


class RebatchExecutor(AbstractExecutor):
    """
    Rebatch the data pipeline

    Arguments:
        node (AbstractPlan): The Rebatch Plan

    """

    def __init__(self, db: EvaDBDatabase, node: RebatchPlan):
        super().__init__(db, node)
        self.batch_mem_size = node.batch_mem_size
        self.batch_size = node.batch_size

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_iter = self.children[0].exec(**kwargs)

        # Calculate the proper batch size, use the smaller one when both batch_mem_size and batch_size are set.
        first_batch = next(child_iter)
        sample_size = get_size(first_batch[:1])
        batch_size = int(min(self.batch_size, self.batch_mem_size / sample_size))
        batch_size = max(1, batch_size)

        current_size = 0
        current_batches = []
        for batch in itertools.chain((first_batch for _ in (0,)), child_iter):
            current_batches.append(batch)
            current_size += len(batch)
            if batch_size <= current_size:
                one_batch = Batch.concat(current_batches, copy=False)
                pos = 0
                while pos + batch_size <= current_size:
                    new_batch = one_batch[pos : pos + batch_size]
                    new_batch.reset_index()
                    yield new_batch
                    pos += batch_size
                if pos < current_size:
                    current_batches = [one_batch[pos:]]
                    current_size = len(current_batches[0])
                else:
                    current_batches = []
                    current_size = 0
        last_batch = Batch.concat(current_batches, copy=False)
        yield last_batch
