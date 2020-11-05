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
from src.optimizer.generators.seq_scan_generator import ScanGenerator
from src.optimizer.generators.insert_generator import InsertGenerator
from src.optimizer.generators.create_generator import CreateGenerator
from src.optimizer.generators.create_udf_generator import CreateUDFGenerator
from src.optimizer.generators.load_generator import LoadDataGenerator
from src.optimizer.operators import Operator, OperatorType
from src.optimizer.optimizer_context import OptimizerContext
from src.optimizer.optimizer_tasks import TopDownRewrite, OptimizeGroup, BottomUpRewrite
from src.optimizer.optimizer_task_stack import OptimizerTaskStack
from src.optimizer.property import PropertyType


class PlanGenerator:
    """
    Used for building Physical Plan from Logical Plan.
    NOTE: This currently just does node transformation. Optimizer logic
    needs to be incorporated.
    """
    _SCAN_NODE_TYPES = (OperatorType.LOGICALFILTER, OperatorType.LOGICALGET,
                        OperatorType.LOGICALPROJECT, OperatorType.LOGICALUNION)
    _INSERT_NODE_TYPE = OperatorType.LOGICALINSERT
    _CREATE_NODE_TYPE = OperatorType.LOGICALCREATE
    _CREATE_UDF_NODE_TYPE = OperatorType.LOGICALCREATEUDF
    _LOAD_NODE_TYPE = OperatorType.LOGICALLOADDATA

    def execute_task_stack(self, task_stack: OptimizerTaskStack):
        while not task_stack.empty():
            task = task_stack.pop()
            task.execute()

    def build_optimal_physical_plan(self, root_grp_id: int, optimizer_context: OptimizerContext):
        physical_plan = None
        root_grp = optimizer_context.memo.get_group(root_grp_id)
        best_grp_expr = root_grp.get_best_expr(PropertyType.DEFAULT)

        physical_plan = best_grp_expr.opr

        for child_grp_id in best_grp_expr.children:
            child_plan = self.build_optimal_physical_plan(child_grp_id, optimizer_context)
            physical_plan.append_child(child_plan)

        return physical_plan

    def optimize(self, logical_plan: Operator):
        optimizer_context = OptimizerContext()
        memo = optimizer_context.memo
        grp_expr = optimizer_context.xform_opr_to_group_expr(logical_plan, False)
        root_grp_id = grp_expr.group_id
        """
        for g in optimizer_context.memo._groups:
            for expr in g._logical_exprs:
                print(expr)
        """
        # TopDown Rewrite
        optimizer_context.task_stack.push(TopDownRewrite(grp_expr, optimizer_context))
        self.execute_task_stack(optimizer_context.task_stack)
        optimizer_context.task_stack.push(BottomUpRewrite(grp_expr, optimizer_context))
        self.execute_task_stack(optimizer_context.task_stack)

        """
        print('-------------------We are done logical rewriter-----------\n')
        for g in optimizer_context.memo._groups:
            for expr in g._logical_exprs:
                print(expr)
        """
        # Optimize Expression (logical -> physical transformation)
        optimizer_context.task_stack.push(OptimizeGroup(root_grp_id, optimizer_context))
        self.execute_task_stack(optimizer_context.task_stack)

        # Build Optimal Tree
        optimal_plan = self.build_optimal_physical_plan(root_grp_id, optimizer_context)
        return optimal_plan

    def build(self, logical_plan: Operator):
        # apply optimizations

        return self.optimize(logical_plan)

        #############################################
        # remove this code once done with optimizer
        if logical_plan.opr_type in self._SCAN_OPR_TYPES:
            return ScanGenerator().build(logical_plan)
        if logical_plan.opr_type is self._INSERT_OPR_TYPE:
            return InsertGenerator().build(logical_plan)
        if logical_plan.opr_type is self._CREATE_OPR_TYPE:
            return CreateGenerator().build(logical_plan)
        if logical_plan.opr_type is self._CREATE_UDF_OPR_TYPE:
            return CreateUDFGenerator().build(logical_plan)
        if logical_plan.opr_type is self._LOAD_OPR_TYPE:
            return LoadDataGenerator().build(logical_plan)
        ###############################################
