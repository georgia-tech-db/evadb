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
# from eva.executor.abstract_executor import UPSTREAM_BATCH
# from eva.planner.nested_loop_join_plan import NestedLoopJoin
from eva.parser.types import JoinType
from eva.planner.lateral_join_build_plan import LateralJoinBuildPlan

# from eva.utils.metrics import Metrics


class LateralJoinExecutor(AbstractExecutor):
    """
    Nested Loop Join executor:
    Returns the tuple joined from inner and outer tuples which
    satisfies the predicate clause.
    It scans the inner relation to join with current outer tuple.

    Arguments:
        node (AbstractPlan): The NestedLoopJoin

    """

    def __init__(self, node: LateralJoinBuildPlan):
        super().__init__(node)
        self.predicate = node.predicate
        self.join_type = node.join_type
        self.join_project = node.join_project
        # self.join_keys = node.join_keys

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:

        outer = self.children[0]
        inner = self.children[1]

        for outer_batch in outer.exec():
            for result_batch in inner.exec(lateral_input=outer_batch):
                if not result_batch.empty() and self.predicate is not None:
                    outcomes = self.predicate.evaluate(result_batch).frames
                    result_batch = Batch(
                        result_batch.frames[(outcomes > 0).to_numpy()].reset_index(
                            drop=True))
            # Then do project
            if not result_batch.empty() and self.join_project is not None:
                batches = [expr.evaluate(result_batch)
                        for expr in self.join_project]
                result_batch = Batch.merge_column_wise(batches)
            
            if not result_batch.empty():
                return result_batch


        # for outer_batch in outer.exec():
        #     cumm_inner_batches = []
        #     if self.join_type == JoinType.LATERAL_JOIN:
        #         self.join_keys =
        #         for inner_batch in inner.exec(lateral_input=outer_batch):
        #             cumm_inner_batches.append(inner_batch)
        #     else:
        #         for inner_batch in inner.exec():
        #             cumm_inner_batches.append(inner_batch)

        #     cumm_inner_batch = Batch.concat(cumm_inner_batches)
        #     # build hash for the inner table
        #     cumm_inner_batch.frames.index = cumm_inner_batch.frames[self.join_keys].apply(
        #         lambda x: hash(tuple(x)), axis=1)
        #     # print('Mat size: ', cumm_inner_batch.batch_size)
        #     # build hash for the outer table
        #     outer_batch.frames.index = outer_batch.frames[self.join_on].apply(
        #         lambda x: hash(tuple(x)), axis=1)
        #     # print(outer_batch.frames.id)
        #     if self.join_type == JoinType.LEFT_JOIN:
        #         join_batch = outer_batch.frames.merge(
        #             cumm_inner_batch.frames, left_index=True, right_index=True, how='left')
        #     else:
        #         join_batch = outer_batch.frames.merge(
        #             cumm_inner_batch.frames, left_index=True, right_index=True)
        #     print('Join size: ', len(join_batch))
        #     join_batch = join_batch.loc[:, ~
        #                                 join_batch.columns.str.endswith('_y')]
        #     join_batch.columns = join_batch.columns.str.rstrip('_x')

        #     # print('hash join ', len(join_batch))
        #     join_batch.reset_index(drop=True, inplace=True)
        #     join_batch = Batch(join_batch)
        #     if not join_batch.empty() and self.predicate is not None:
        #         outcomes = self.predicate.evaluate(join_batch).frames
        #         # print(cumm_join_batch.frames[cumm_join_batch.frames['labels']=='person'])
        #         join_batch = Batch(
        #             join_batch.frames[(outcomes > 0).to_numpy()].reset_index(
        #                 drop=True))
        #     # Then do project
        #     if not join_batch.empty() and self.join_project is not None:
        #         batches = [expr.evaluate(join_batch)
        #                    for expr in self.join_project]
        #         join_batch = Batch.merge_column_wise(batches)

        #     Metrics().stop_perf(f'HASH JOIN')

        #     yield join_batch
