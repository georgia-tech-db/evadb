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
from eva.catalog.catalog_manager import CatalogManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError, handle_if_not_exists
from eva.expression.abstract_expression import ExpressionType
from eva.parser.create_statement import ColumnDefinition
from eva.plan_nodes.create_mat_view_plan import CreateMaterializedViewPlan
from eva.plan_nodes.types import PlanOprType
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


class CreateMaterializedViewExecutor(AbstractExecutor):
    def __init__(self, node: CreateMaterializedViewPlan):
        super().__init__(node)
        self.catalog = CatalogManager()

    def validate(self):
        pass

    def exec(self):
        """Create materialized view executor"""
        if not handle_if_not_exists(self.node.view, self.node.if_not_exists):
            child = self.children[0]
            project_cols = None
            # only support seq scan based materialization
            if child.node.opr_type == PlanOprType.SEQUENTIAL_SCAN:
                project_cols = child.project_expr
            elif child.node.opr_type == PlanOprType.PROJECT:
                project_cols = child.target_list
            else:
                err_msg = "Invalid query {}, expected {} or {}".format(
                    child.node.opr_type,
                    PlanOprType.SEQUENTIAL_SCAN,
                    PlanOprType.PROJECT,
                )

                logger.error(err_msg)
                raise ExecutorError(err_msg)

            # gather child projected column objects
            child_objs = []
            for child_col in project_cols:
                if child_col.etype == ExpressionType.TUPLE_VALUE:
                    child_objs.append(child_col.col_object)
                elif child_col.etype == ExpressionType.FUNCTION_EXPRESSION:
                    child_objs.extend(child_col.output_objs)

            # Number of projected columns should be equal to mat view columns
            if len(self.node.columns) != len(child_objs):
                err_msg = "# projected columns mismatch, expected {} found {}\
                ".format(
                    len(self.node.columns), len(child_objs)
                )
                logger.error(err_msg)
                raise ExecutorError(err_msg)

            col_defs = []
            # Copy column type info from child columns
            for idx, child_col_obj in enumerate(child_objs):
                col = self.node.columns[idx]
                col_defs.append(
                    ColumnDefinition(
                        col.name,
                        child_col_obj.type,
                        child_col_obj.array_type,
                        child_col_obj.array_dimensions,
                    )
                )

            view_catalog_entry = self.catalog.create_and_insert_table_catalog_entry(
                self.node.view, col_defs
            )
            storage_engine = StorageEngine.factory(view_catalog_entry)
            storage_engine.create(table=view_catalog_entry)

            # Populate the view
            for batch in child.exec():
                batch.drop_column_alias()
                storage_engine.write(view_catalog_entry, batch)
