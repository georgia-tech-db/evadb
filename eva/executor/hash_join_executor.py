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

from eva.models.storage.batch import Batch
from eva.executor.abstract_executor import AbstractExecutor
from eva.planner.hash_join_probe_plan import HashJoinProbePlan


class HashJoinExecutor(AbstractExecutor):

    def __init__(self, node: HashJoinProbePlan):
        super().__init__(node)
        self.predicate = node.join_predicate
        self.join_type = node.join_type
        self.probe_keys = node.probe_keys
        self.join_project = node.join_project

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:

        build_table = self.children[0]
        probe_table = self.children[1]
        hash_keys = [key.col_alias for key in self.probe_keys]
        for build_batch in build_table.exec():
            for probe_batch in probe_table.exec():
                probe_batch.frames.index = probe_batch.frames[
                    hash_keys].apply(
                    lambda x: hash(tuple(x)), axis=1)
                join_batch = probe_batch.frames.merge(build_batch.frames,
                                                      left_index=True,
                                                      right_index=True,
                                                      how='inner')
                join_batch.reset_index(drop=True, inplace=True)
                join_batch = Batch(join_batch)
                if not join_batch.empty() and self.predicate:
                    outcomes = self.predicate.evaluate(join_batch).frames
                    filtered_df = join_batch.frames[(outcomes > 0).to_numpy()]
                    join_batch = Batch(filtered_df.reset_index(drop=True))
                # Then do project
                if not join_batch.empty() and self.join_project:
                    batches = [expr.evaluate(join_batch)
                               for expr in self.join_project]
                    join_batch = Batch.merge_column_wise(batches)

                yield join_batch
