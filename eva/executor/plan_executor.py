# coding=utf-8
# Copyright 2018-2023 EVA
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

from eva.database import EVADB
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.apply_and_merge_executor import ApplyAndMergeExecutor
from eva.executor.create_executor import CreateExecutor
from eva.executor.create_index_executor import CreateIndexExecutor
from eva.executor.create_mat_view_executor import CreateMaterializedViewExecutor
from eva.executor.create_udf_executor import CreateUDFExecutor
from eva.executor.delete_executor import DeleteExecutor
from eva.executor.drop_executor import DropExecutor
from eva.executor.drop_udf_executor import DropUDFExecutor
from eva.executor.executor_utils import ExecutorError
from eva.executor.explain_executor import ExplainExecutor
from eva.executor.function_scan_executor import FunctionScanExecutor
from eva.executor.groupby_executor import GroupByExecutor
from eva.executor.hash_join_executor import HashJoinExecutor
from eva.executor.insert_executor import InsertExecutor
from eva.executor.join_build_executor import BuildJoinExecutor
from eva.executor.lateral_join_executor import LateralJoinExecutor
from eva.executor.limit_executor import LimitExecutor
from eva.executor.load_executor import LoadDataExecutor
from eva.executor.nested_loop_join_executor import NestedLoopJoinExecutor
from eva.executor.orderby_executor import OrderByExecutor
from eva.executor.pp_executor import PPExecutor
from eva.executor.predicate_executor import PredicateExecutor
from eva.executor.project_executor import ProjectExecutor
from eva.executor.rename_executor import RenameExecutor
from eva.executor.sample_executor import SampleExecutor
from eva.executor.seq_scan_executor import SequentialScanExecutor
from eva.executor.show_info_executor import ShowInfoExecutor
from eva.executor.storage_executor import StorageExecutor
from eva.executor.union_executor import UnionExecutor
from eva.executor.vector_index_scan_executor import VectorIndexScanExecutor
from eva.experimental.parallel.executor.exchange_executor import ExchangeExecutor
from eva.models.storage.batch import Batch
from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.plan_nodes.types import PlanOprType
from eva.utils.logging_manager import logger


class PlanExecutor:
    """
    This is an interface between plan tree and execution tree.
    We traverse the plan tree and build execution tree from it

    Arguments:
        plan (AbstractPlan): Physical plan tree which needs to be executed
        evadb (EVADB): database to execute the query on
    """

    def __init__(self, evadb: EVADB, plan: AbstractPlan):
        self._db = evadb
        self._plan = plan

    def _build_execution_tree(self, plan: AbstractPlan) -> AbstractExecutor:
        """build the execution tree from plan tree

        Arguments:
            plan {AbstractPlan} -- Input Plan tree

        Returns:
            AbstractExecutor -- Compiled Execution tree
        """
        root = None
        if plan is None:
            return root

        # Get plan node type
        plan_opr_type = plan.opr_type

        if plan_opr_type == PlanOprType.SEQUENTIAL_SCAN:
            executor_node = SequentialScanExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.UNION:
            executor_node = UnionExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.STORAGE_PLAN:
            executor_node = StorageExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.PP_FILTER:
            executor_node = PPExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.CREATE:
            executor_node = CreateExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.RENAME:
            executor_node = RenameExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.DROP:
            executor_node = DropExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.INSERT:
            executor_node = InsertExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.CREATE_UDF:
            executor_node = CreateUDFExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.DROP_UDF:
            executor_node = DropUDFExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.LOAD_DATA:
            executor_node = LoadDataExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.GROUP_BY:
            executor_node = GroupByExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.ORDER_BY:
            executor_node = OrderByExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.LIMIT:
            executor_node = LimitExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.SAMPLE:
            executor_node = SampleExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.NESTED_LOOP_JOIN:
            executor_node = NestedLoopJoinExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.LATERAL_JOIN:
            logger.warn(
                "LateralJoin Executor should not be part of the execution plan."
                "Please raise an issue with the current query. Thanks!"
            )
            executor_node = LateralJoinExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.HASH_JOIN:
            executor_node = HashJoinExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.HASH_BUILD:
            executor_node = BuildJoinExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.FUNCTION_SCAN:
            executor_node = FunctionScanExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.CREATE_MATERIALIZED_VIEW:
            executor_node = CreateMaterializedViewExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.EXCHANGE:
            executor_node = ExchangeExecutor(db=self._db, node=plan)
            inner_executor = self._build_execution_tree(plan.inner_plan)
            executor_node.build_inner_executor(inner_executor)
        elif plan_opr_type == PlanOprType.PROJECT:
            executor_node = ProjectExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.PREDICATE_FILTER:
            executor_node = PredicateExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.SHOW_INFO:
            executor_node = ShowInfoExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.EXPLAIN:
            executor_node = ExplainExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.CREATE_INDEX:
            executor_node = CreateIndexExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.APPLY_AND_MERGE:
            executor_node = ApplyAndMergeExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.VECTOR_INDEX_SCAN:
            executor_node = VectorIndexScanExecutor(db=self._db, node=plan)
        elif plan_opr_type == PlanOprType.DELETE:
            executor_node = DeleteExecutor(db=self._db, node=plan)

        # EXPLAIN does not need to build execution tree for its children
        if plan_opr_type != PlanOprType.EXPLAIN:
            # Build Executor Tree for children
            for children in plan.children:
                executor_node.append_child(self._build_execution_tree(children))

        return executor_node

    def execute_plan(self) -> Iterator[Batch]:
        """execute the plan tree"""
        try:
            execution_tree = self._build_execution_tree(self._plan)
            output = execution_tree.exec()
            if output is not None:
                yield from output
        except Exception as e:
            logger.exception(str(e))
            raise ExecutorError(e)
