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

from src.catalog.catalog_manager import CatalogManager
from src.planner.create_mat_view_plan import CreateMaterializedViewPlan
from src.planner.types import PlanOprType
from src.executor.abstract_executor import AbstractExecutor
from src.utils.generic_utils import generate_file_path
from src.storage.storage_engine import StorageEngine
from src.expression.abstract_expression import ExpressionType

from src.utils.logging_manager import LoggingManager, LoggingLevel


class CreateMaterializedViewExecutor(AbstractExecutor):

    def __init__(self, node: CreateMaterializedViewPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """Create materialized view executor
        """
        # Create the view table
        table_name = self.node.view.table_info.table_name
        file_url = str(generate_file_path(table_name))
        # Extract the column types from the child node
        child = self.children[0]
        # only support seq scan based materialization
        if child.node.opr_type != PlanOprType.SEQUENTIAL_SCAN:
            LoggingManager().log('Invalid query {}, expected {}',
                                 child.node.opr_type,
                                 PlanOprType.SEQUENTIAL_SCAN,
                                 LoggingLevel.ERROR)
        if len(self.node.col_list) != len(child.project_expr):
            LoggingManager().log('# projected columns mismatch, expected {} \
            found {}'.format(len(self.node.col_list),
                             len(child.project_expr)),
                LoggingLevel.ERROR)

        col_metainfo_list = []
        catalog = CatalogManager()
        for col_def, child_col in zip(self.node.col_list, child.project_expr):
            col_obj = None
            if child_col.etype == ExpressionType.TUPLE_VALUE:
                col_obj = child_col.col_object
            elif child_col.etype == ExpressionType.FUNCTION_EXPRESSION:
                col_obj = child_col.output_obj
            
            col_metainfo_list.append(catalog.create_column_metadata(
                col_def.name, col_obj.type, col_obj.array_dimensions))

        view_metainfo = CatalogManager().create_metadata(table_name,
                                                         file_url,
                                                         col_metainfo_list)
        StorageEngine.create(view_metainfo)

        # Populate the view
        for batch in child.exec():
            StorageEngine.write(view_metainfo, batch)
