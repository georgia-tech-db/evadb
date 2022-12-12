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
from eva.planner.create_mat_view_plan import CreateMaterializedViewPlan
from eva.planner.types import PlanOprType
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger
from eva.catalog.catalog_type import ColumnType, NdArrayType


class CreateMaterializedViewExecutor(AbstractExecutor):
    def __init__(self, node: CreateMaterializedViewPlan):
        super().__init__(node)
        self.catalog = CatalogManager()

    def validate(self):
        pass

    def exec(self, *args, **kwargs):
        """Create materialized view executor"""
      
        child = self.children[0]
        project_cols = None

        # only support seq scan/project/function scan
        if child.node.opr_type == PlanOprType.SEQUENTIAL_SCAN:
            project_cols = child.project_expr
        elif child.node.opr_type == PlanOprType.PROJECT:
            project_cols = child.target_list
        elif child.node.opr_type == PlanOprType.FUNCTION_SCAN:
            pass
        else:
            err_msg = "Invalid query {}, expected {} or {} or {}".format(
                child.node.opr_type,
                PlanOprType.SEQUENTIAL_SCAN,
                PlanOprType.PROJECT,
                PlanOprType.FUNCTION_SCAN
            )

            logger.error(err_msg)
            raise ExecutorError(err_msg)


        if not handle_if_not_exists(self.node.view.table, self.node.if_not_exists):
            
            # TODO: Temporarily handling the case of materialized view creation separately
            if child.node.opr_type == PlanOprType.FUNCTION_SCAN:

                # hardcode the col info as id for now
                col_defs = [
                    ColumnDefinition(
                        col_name="frame_id",
                        col_type=ColumnType.INTEGER,
                        col_array_type=NdArrayType.ANYTYPE,
                        col_dim=[]
                    )
                ]

                for op_obj in child.func_expr.output_objs:
                    col_defs.append(
                        ColumnDefinition(
                            col_name=op_obj.name,
                            col_type=op_obj.type,
                            col_array_type=op_obj.array_type,
                            col_dim=op_obj.array_dimensions
                        )
                    )
            else:
                
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

            view_metainfo = self.catalog.create_table_metadata(self.node.view.table, col_defs)
            storage_engine = StorageEngine.factory(view_metainfo)
            storage_engine.create(table=view_metainfo)

        # If view already exists, get the metainfo
        else:
            view_metainfo = self.catalog.get_dataset_metadata(
                database_name="", 
                dataset_name=self.node.view.table.table_name
            )

        # Populate the view
        for batch in child.exec(*args, **kwargs):
            batch.drop_column_alias()
            storage_engine.write(view_metainfo, batch)
            if self.node.yield_output:
                yield batch