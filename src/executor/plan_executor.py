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
from src.query_executor.abstract_executor import AbstractExecutor
from src.query_executor.seq_scan_executor import SequentialScanExecutor
from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanNodeType
from src.query_executor.disk_based_storage_executor import DiskStorageExecutor
from src.query_executor.pp_executor import PPExecutor


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
        plan_node_type = plan.node_type

        if plan_node_type == PlanNodeType.SEQUENTIAL_SCAN:
            executor_node = SequentialScanExecutor(node=plan)
        elif plan_node_type == PlanNodeType.STORAGE_PLAN:
            executor_node = DiskStorageExecutor(node=plan)
        elif plan_node_type == PlanNodeType.PP_FILTER:
            executor_node = PPExecutor(node=plan)

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

        output_batches = []

        for batch in execution_tree.next():
            output_batches.append(batch)

        self._clean_execution_tree(execution_tree)
        return output_batches
