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

from eva.parser.create_statement import ColumnDefinition
from eva.planner.create_mat_view_plan import CreateMaterializedViewPlan
from eva.planner.types import PlanOprType
from eva.executor.abstract_executor import AbstractExecutor
from eva.storage.storage_engine import StorageEngine
from eva.expression.abstract_expression import ExpressionType
from eva.optimizer.optimizer_utils import (create_table_metadata,
                                           check_table_exists)
from eva.utils.logging_manager import LoggingManager, LoggingLevel


class CreateMaterializedViewExecutor(AbstractExecutor):

    def __init__(self, node: CreateMaterializedViewPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """Create materialized view executor
        """
        if not check_table_exists(self.node.view,
                                  self.node.if_not_exists):
            child = self.children[0]
            # only support seq scan based materialization
            if child.node.opr_type != PlanOprType.SEQUENTIAL_SCAN:
                err_msg = 'Invalid query {}, expected {}'.format(
                    child.node.opr_type, PlanOprType.SEQUENTIAL_SCAN)

                LoggingManager().log(err_msg, LoggingLevel.ERROR)
                raise RuntimeError(err_msg)
            if len(self.node.columns) != len(child.project_expr):
                err_msg = '# projected columns mismatch, expected {} found {}\
                '.format(len(self.node.columns), len(child.project_expr))
                LoggingManager().log(err_msg, LoggingLevel.ERROR)
                raise RuntimeError(err_msg)

            col_defs = []
            # Copy column type info from child columns
            for idx, child_col in enumerate(child.project_expr):
                col = self.node.columns[idx]
                col_obj = None
                if child_col.etype == ExpressionType.TUPLE_VALUE:
                    col_obj = child_col.col_object
                elif child_col.etype == ExpressionType.FUNCTION_EXPRESSION:
                    col_obj = child_col.output_obj

                col_defs.append(ColumnDefinition(
                    col.name,
                    col_obj.type,
                    col_obj.array_type,
                    col_obj.array_dimensions))

            view_metainfo = create_table_metadata(
                self.node.view, col_defs)
            StorageEngine.create(table=view_metainfo)

            # Populate the view
            for batch in child.exec():
                StorageEngine.write(view_metainfo, batch)
