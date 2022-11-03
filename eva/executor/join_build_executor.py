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
from typing import Iterator

from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.hash_join_build_plan import HashJoinBuildPlan


class BuildJoinExecutor(AbstractExecutor):
    def __init__(self, node: HashJoinBuildPlan):
        super().__init__(node)
        self.predicate = None  # node.join_predicate
        self.join_type = node.join_type
        self.build_keys = node.build_keys

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]
        # build in memory hash table and pass to the probe phase
        # Assumption the hash table fits in memory
        # Todo: Implement a partition based hash join (grace hash join)
        cumm_batches = [batch for batch in child_executor.exec() if not batch.empty()]
        cumm_batches = Batch.concat(cumm_batches)
        hash_keys = [key.col_alias for key in self.build_keys]
        cumm_batches.reassign_indices_to_hash(hash_keys)
        yield cumm_batches
