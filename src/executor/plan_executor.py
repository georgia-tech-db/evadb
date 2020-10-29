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
import pandas as pd

from src.executor.abstract_executor import AbstractExecutor
from src.executor.seq_scan_executor import SequentialScanExecutor
from src.models.storage.batch import Batch
from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanOprType
from src.executor.pp_executor import PPExecutor
from src.executor.create_executor import CreateExecutor
from src.executor.insert_executor import InsertExecutor
from src.executor.create_udf_executor import CreateUDFExecutor
from src.executor.load_executor import LoadDataExecutor
from src.executor.storage_executor import StorageExecutor
from src.executor.union_executor import UnionExecutor
from src.executor.create_mat_view_executor import \
    CreateMaterializedViewExecutor


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
        elif plan_opr_type == PlanOprType.INSERT:
            executor_node = InsertExecutor(node=plan)
        elif plan_opr_type == PlanOprType.CREATE_UDF:
            executor_node = CreateUDFExecutor(node=plan)
        elif plan_opr_type == PlanOprType.LOAD_DATA:
            executor_node = LoadDataExecutor(node=plan)
        elif plan_opr_type == PlanOprType.CREATE_MATERIALIZED_VIEW:
            executor_node = CreateMaterializedViewExecutor(node=plan)

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

    def execute_plan(self):
        """execute the plan tree

        """
        # TODO: for now this returns list of batch frames. Update to return
        # a stitched output
        execution_tree = self._build_execution_tree(self._plan)

        output_batches = Batch(pd.DataFrame())

        # ToDo generalize this logic
        _INSERT_CREATE_LOAD = (
            PlanOprType.CREATE,
            PlanOprType.INSERT,
            PlanOprType.CREATE_UDF,
            PlanOprType.LOAD_DATA,
            PlanOprType.CREATE_MATERIALIZED_VIEW)
        if execution_tree.node.opr_type in _INSERT_CREATE_LOAD:
            execution_tree.exec()
        else:
            for batch in execution_tree.exec():
                output_batches += batch

        self._clean_execution_tree(execution_tree)
        return output_batches
