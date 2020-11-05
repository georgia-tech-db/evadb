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
from src.catalog.models.df_metadata import DataFrameMetadata
from src.expression.abstract_expression import AbstractExpression
from src.optimizer.operators import (LogicalGet, LogicalFilter, LogicalProject,
                                     LogicalInsert, LogicalCreate,
                                     LogicalCreateUDF, LogicalLoadData,
                                     LogicalQueryDerivedGet, LogicalUnion,
                                     LogicalCreateMaterializedView)
from src.parser.statement import AbstractStatement
from src.parser.select_statement import SelectStatement
from src.parser.insert_statement import InsertTableStatement
from src.parser.create_statement import CreateTableStatement
from src.parser.create_udf_statement import CreateUDFStatement
from src.parser.load_statement import LoadDataStatement
from src.parser.create_mat_view_statement \
    import CreateMaterializedViewStatement
from src.optimizer.optimizer_utils import (bind_table_ref, bind_columns_expr,
                                           bind_predicate_expr,
                                           create_column_metadata,
                                           bind_dataset,
                                           column_definition_to_udf_io,
                                           create_video_metadata)
from src.parser.table_ref import TableRef
from src.utils.logging_manager import LoggingLevel, LoggingManager


class StatementToPlanConvertor:
    def __init__(self):
        self._plan = None
        self._dataset = None
        self._column_map = {}  # key: column_name (str) value: DataFrameColumn

    def _populate_column_map(self, dataset: DataFrameMetadata):
        for column in dataset.columns:
            self._column_map[column.name.lower()] = column

    def visit_table_ref(self, video: TableRef):
        """Bind table ref object and convert to Logical get operator

        Arguments:
            video {TableRef} -- [Input table ref object created by the parser]
        """
        catalog_vid_metadata = bind_dataset(video.table_info)

        self._populate_column_map(catalog_vid_metadata)

        self._plan = LogicalGet(video, catalog_vid_metadata)

    def visit_select(self, statement: SelectStatement):
        """converter for select statement

        Arguments:
            statement {SelectStatement} -- [input select statement]
        """

        video = statement.from_table
        if video is None:
            LoggingManager().log('From entry missing in select statement',
                                 LoggingLevel.ERROR)
            return None

        if isinstance(video, SelectStatement):
            # NestedQuery
            self.visit_select(video)
            child_plan = self._plan
            self._plan = LogicalQueryDerivedGet()
            self._plan.append_child(child_plan)
        elif isinstance(video, TableRef):
            # Table
            self.visit_table_ref(video)

        # Filter Operator
        predicate = statement.where_clause
        if predicate is not None:
            self._visit_select_predicate(predicate)

        # Projection operator
        select_columns = statement.target_list

        # ToDO
        # add support for SELECT STAR
        if select_columns is not None:
            self._visit_projection(select_columns)

        # union
        if statement.union_link is not None:
            self._visit_union(statement.union_link, statement.union_all)

    def _visit_union(self, target, all):
        left_child_plan = self._plan
        self.visit_select(target)
        right_child_plan = self._plan
        self._plan = LogicalUnion(all=all)
        self._plan.append_child(left_child_plan)
        self._plan.append_child(right_child_plan)

    def _visit_projection(self, select_columns):
        # Bind the columns using catalog
        bind_columns_expr(select_columns, self._column_map)
        projection_opr = LogicalProject(select_columns)
        projection_opr.append_child(self._plan)
        self._plan = projection_opr

    def _visit_select_predicate(self, predicate: AbstractExpression):
        # Binding the expression
        bind_predicate_expr(predicate, self._column_map)
        filter_opr = LogicalFilter(predicate)
        filter_opr.append_child(self._plan)
        self._plan = filter_opr

    def visit_insert(self, statement: AbstractStatement):
        """Converter for parsed insert statement

        Arguments:
            statement {AbstractStatement} -- [input insert statement]
        """
        # Bind the table reference
        video = statement.table
        catalog_table_id = bind_table_ref(video.table_info)

        # Bind column_list
        col_list = statement.column_list
        for col in col_list:
            if col.table_name is None:
                col.table_name = video.table_info.table_name
            if col.table_metadata_id is None:
                col.table_metadata_id = catalog_table_id
        bind_columns_expr(col_list, {})

        # Nothing to be done for values as we add support for other variants of
        # insert we will handle them
        value_list = statement.value_list

        # Ready to create Logical node
        insert_opr = LogicalInsert(
            video, catalog_table_id, col_list, value_list)
        self._plan = insert_opr

    def visit_create(self, statement: AbstractStatement):
        """Convertor for parsed insert Statement

        Arguments:
            statement {AbstractStatement} -- [Create statement]
        """
        video_ref = statement.table_ref
        if video_ref is None:
            LoggingManager().log("Missing Table Name In Create Statement",
                                 LoggingLevel.ERROR)

        if_not_exists = statement.if_not_exists
        column_metadata_list = create_column_metadata(statement.column_list)

        create_opr = LogicalCreate(
            video_ref, column_metadata_list, if_not_exists)
        self._plan = create_opr

    def visit_create_udf(self, statement: CreateUDFStatement):
        """Convertor for parsed create udf statement

        Arguments:
            statement {CreateUDFStatement} -- Create UDF Statement
        """
        annotated_inputs = column_definition_to_udf_io(statement.inputs, True)
        annotated_outputs = column_definition_to_udf_io(
            statement.outputs, False)

        create_udf_opr = LogicalCreateUDF(statement.name,
                                          statement.if_not_exists,
                                          annotated_inputs, annotated_outputs,
                                          statement.impl_path,
                                          statement.udf_type)
        self._plan = create_udf_opr

    def visit_load_data(self, statement: LoadDataStatement):
        """Convertor for parsed load data statement
        If the input table already exists we return its
        metadata. Else we will create a new metadata object for this
        table name.
        Arguments:
            statement(LoadDataStatement): [Load data statement]
        """
        table = statement.table
        table_metainfo = bind_dataset(table.table_info)
        if table_metainfo is None:
            # Create a new metadata object
            table_metainfo = create_video_metadata(table.table_info.table_name)

        load_data_opr = LogicalLoadData(table_metainfo, statement.path)
        self._plan = load_data_opr

    def visit_materialized_view(self,
                                statement: CreateMaterializedViewStatement):
        if statement.view_ref is None:
            LoggingManager().log("Missing View Name In Create Materialized \
                                    View Statement", LoggingLevel.ERROR)
        if statement.query is None:
            LoggingManager().log("Missing query in Create Materialized \
                                    View Statement", LoggingLevel.ERROR)
        mat_view_opr = LogicalCreateMaterializedView(
            statement.view_ref, statement.col_list, statement.if_not_exists)

        self.visit_select(statement.query)
        mat_view_opr.append_child(self._plan)
        self._plan = mat_view_opr

    def visit(self, statement: AbstractStatement):
        """Based on the instance of the statement the corresponding
           visit is called.
           The logic is hidden from client.

        Arguments:
            statement {AbstractStatement} -- [Input statement]
        """
        if isinstance(statement, SelectStatement):
            self.visit_select(statement)
        elif isinstance(statement, InsertTableStatement):
            self.visit_insert(statement)
        elif isinstance(statement, CreateTableStatement):
            self.visit_create(statement)
        elif isinstance(statement, CreateUDFStatement):
            self.visit_create_udf(statement)
        elif isinstance(statement, LoadDataStatement):
            self.visit_load_data(statement)
        elif isinstance(statement, CreateMaterializedViewStatement):
            self.visit_materialized_view(statement)
        return self._plan

    @property
    def plan(self):
        return self._plan
