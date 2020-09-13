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
from src.optimizer.optimizer_tasks import TopDownRewrite


class PlanGenerator:
    """
    Used for building Physical Plan from Logical Plan.
    NOTE: This currently just does node transformation. Optimizer logic
    needs to be incorporated.
    """
    _SCAN_NODE_TYPES = (OperatorType.LOGICALFILTER, OperatorType.LOGICALGET,
                        OperatorType.LOGICALPROJECT)
    _INSERT_NODE_TYPE = OperatorType.LOGICALINSERT
    _CREATE_NODE_TYPE = OperatorType.LOGICALCREATE
    _CREATE_UDF_NODE_TYPE = OperatorType.LOGICALCREATEUDF
    _LOAD_NODE_TYPE = OperatorType.LOGICALLOADDATA

    def optimize(self, logical_plan: Operator):
        optimizer_context = OptimizerContext()
        memo = optimizer_context.memo
        grp_expr = optimizer_context.xform_opr_to_group_expr(logical_plan)

        # TopDown Rewrite
        TopDownRewrite(grp_expr, optimizer_context).execute()
        
        # Optimization
        

    def build(self, logical_plan: Operator):
        # apply optimizations

        self.optimize(logical_plan)

        #############################################
        # remove this code once done with optimizer
        if logical_plan.type in self._SCAN_NODE_TYPES:
            return ScanGenerator().build(logical_plan)
        if logical_plan.type is self._INSERT_NODE_TYPE:
            return InsertGenerator().build(logical_plan)
        if logical_plan.type is self._CREATE_NODE_TYPE:
            return CreateGenerator().build(logical_plan)
        if logical_plan.type is self._CREATE_UDF_NODE_TYPE:
            return CreateUDFGenerator().build(logical_plan)
        if logical_plan.type is self._LOAD_NODE_TYPE:
            return LoadDataGenerator().build(logical_plan)
        ###############################################
