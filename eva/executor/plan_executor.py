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
from eva.executor.create_executor import CreateExecutor
from eva.executor.create_mat_view_executor import CreateMaterializedViewExecutor
from eva.executor.create_udf_executor import CreateUDFExecutor
from eva.executor.drop_executor import DropExecutor
from eva.executor.drop_udf_executor import DropUDFExecutor
from eva.executor.explain_executor import ExplainExecutor
from eva.executor.function_scan_executor import FunctionScanExecutor
from eva.executor.groupby_executor import GroupByExecutor
from eva.executor.hash_join_executor import HashJoinExecutor
from eva.executor.insert_executor import InsertExecutor
from eva.executor.join_build_executor import BuildJoinExecutor
from eva.executor.lateral_join_executor import LateralJoinExecutor
from eva.executor.limit_executor import LimitExecutor
from eva.executor.load_executor import LoadDataExecutor
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
from eva.executor.upload_executor import UploadExecutor
from eva.experimental.ray.executor.exchange_executor import ExchangeExecutor
from eva.models.storage.batch import Batch
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class PlanExecutor:
    """
    This is an interface between plan tree and execution tree.
    We traverse the plan tree and build execution tree from it

    Arguments:
        plan (AbstractPlan): Physical plan tree which needs to be executed

    """

    def __init__(self, plan: AbstractPlan):
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
            executor_node = SequentialScanExecutor(node=plan)
        elif plan_opr_type == PlanOprType.UNION:
            executor_node = UnionExecutor(node=plan)
        elif plan_opr_type == PlanOprType.STORAGE_PLAN:
            executor_node = StorageExecutor(node=plan)
        elif plan_opr_type == PlanOprType.PP_FILTER:
            executor_node = PPExecutor(node=plan)
        elif plan_opr_type == PlanOprType.CREATE:
            executor_node = CreateExecutor(node=plan)
        elif plan_opr_type == PlanOprType.RENAME:
            executor_node = RenameExecutor(node=plan)
        elif plan_opr_type == PlanOprType.DROP:
            executor_node = DropExecutor(node=plan)
        elif plan_opr_type == PlanOprType.INSERT:
            executor_node = InsertExecutor(node=plan)
        elif plan_opr_type == PlanOprType.CREATE_UDF:
            executor_node = CreateUDFExecutor(node=plan)
        elif plan_opr_type == PlanOprType.DROP_UDF:
            executor_node = DropUDFExecutor(node=plan)
        elif plan_opr_type == PlanOprType.LOAD_DATA:
            executor_node = LoadDataExecutor(node=plan)
        elif plan_opr_type == PlanOprType.UPLOAD:
            executor_node = UploadExecutor(node=plan)
        elif plan_opr_type == PlanOprType.GROUP_BY:
            executor_node = GroupByExecutor(node=plan)
        elif plan_opr_type == PlanOprType.ORDER_BY:
            executor_node = OrderByExecutor(node=plan)
        elif plan_opr_type == PlanOprType.LIMIT:
            executor_node = LimitExecutor(node=plan)
        elif plan_opr_type == PlanOprType.SAMPLE:
            executor_node = SampleExecutor(node=plan)
        elif plan_opr_type == PlanOprType.LATERAL_JOIN:
            executor_node = LateralJoinExecutor(node=plan)
        elif plan_opr_type == PlanOprType.HASH_JOIN:
            executor_node = HashJoinExecutor(node=plan)
        elif plan_opr_type == PlanOprType.HASH_BUILD:
            executor_node = BuildJoinExecutor(node=plan)
        elif plan_opr_type == PlanOprType.FUNCTION_SCAN:
            executor_node = FunctionScanExecutor(node=plan)
        elif plan_opr_type == PlanOprType.CREATE_MATERIALIZED_VIEW:
            executor_node = CreateMaterializedViewExecutor(node=plan)
        elif plan_opr_type == PlanOprType.EXCHANGE:
            executor_node = ExchangeExecutor(node=plan)
        elif plan_opr_type == PlanOprType.PROJECT:
            executor_node = ProjectExecutor(node=plan)
        elif plan_opr_type == PlanOprType.PREDICATE_FILTER:
            executor_node = PredicateExecutor(node=plan)
        elif plan_opr_type == PlanOprType.SHOW_INFO:
            executor_node = ShowInfoExecutor(node=plan)
        elif plan_opr_type == PlanOprType.EXPLAIN:
            executor_node = ExplainExecutor(node=plan)

        # EXPLAIN does not need to build execution tree for its children
        if plan_opr_type != PlanOprType.EXPLAIN:
            # Build Executor Tree for children
            for children in plan.children:
                executor_node.append_child(self._build_execution_tree(children))

        return executor_node

    def _clean_execution_tree(self, tree_root: AbstractExecutor):
        """clean the execution tree from memory

        Arguments:
            tree_root {AbstractExecutor} -- root of execution tree to delete
        """
        # ToDo
        # clear all the nodes from the execution tree

    def execute_plan(self) -> Iterator[Batch]:
        """execute the plan tree"""
        execution_tree = self._build_execution_tree(self._plan)
        output = execution_tree.exec()
        if output is not None:
            yield from output
        self._clean_execution_tree(execution_tree)
