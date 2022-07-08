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

from eva.expression.abstract_expression import AbstractExpression
from eva.optimizer.operators import (LogicalCreateMaterializedView, LogicalGet,
                                     LogicalFilter, LogicalProject,
                                     LogicalCreate,
                                     LogicalDrop,
                                     LogicalCreateUDF, LogicalLoadData,
                                     LogicalUpload, LogicalQueryDerivedGet,
                                     LogicalUnion, LogicalOrderBy,
                                     LogicalLimit, LogicalSample,
                                     LogicalFunctionScan, LogicalJoin)
from eva.parser.statement import AbstractStatement
from eva.parser.select_statement import SelectStatement
from eva.parser.insert_statement import InsertTableStatement
from eva.parser.create_statement import CreateTableStatement
from eva.parser.drop_statement import DropTableStatement
from eva.parser.create_udf_statement import CreateUDFStatement
from eva.parser.create_mat_view_statement \
    import CreateMaterializedViewStatement
from eva.parser.load_statement import LoadDataStatement
from eva.parser.upload_statement import UploadStatement
from eva.optimizer.optimizer_utils import column_definition_to_udf_io
from eva.parser.table_ref import TableRef
from eva.utils.logging_manager import logger


class StatementToPlanConvertor:
    def __init__(self):
        self._plan = None
        self._dataset = None

    def visit_table_ref(self, table_ref: TableRef):
        """Bind table ref object and convert to LogicalGet, LogicalJoin,
            LogicalFunctionScan, or LogicalQueryDerivedGet

        Arguments:
            table {TableRef} - - [Input table ref object created by the parser]
        """
        if table_ref.is_table_atom():
            # Table
            catalog_vid_metadata = table_ref.table.table_obj
            self._plan = LogicalGet(table_ref,
                                    catalog_vid_metadata,
                                    table_ref.alias)

        elif table_ref.is_func_expr():
            self._plan = LogicalFunctionScan(func_expr=table_ref.func_expr)

        elif table_ref.is_select():
            # NestedQuery
            self.visit_select(table_ref.select_statement)
            child_plan = self._plan
            self._plan = LogicalQueryDerivedGet(table_ref.alias)
            self._plan.append_child(child_plan)

        elif table_ref.is_join():
            join_node = table_ref.join_node
            join_plan = LogicalJoin(join_type=join_node.join_type,
                                    join_predicate=join_node.predicate)
            self.visit_table_ref(join_node.left)
            join_plan.append_child(self._plan)
            self.visit_table_ref(join_node.right)
            join_plan.append_child(self._plan)
            self._plan = join_plan

        if table_ref.sample_freq:
            self._visit_sample(table_ref.sample_freq)

    def visit_select(self, statement: SelectStatement):
        """converter for select statement

        Arguments:
            statement {SelectStatement} - - [input select statement]
        """

        table_ref = statement.from_table
        if table_ref is None:
            logger.error('From entry missing in select statement')
            return None

        self.visit_table_ref(table_ref)

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

        if statement.orderby_list is not None:
            self._visit_orderby(statement.orderby_list)

        if statement.limit_count is not None:
            self._visit_limit(statement.limit_count)

    def _visit_sample(self, sample_freq):
        sample_opr = LogicalSample(sample_freq)
        sample_opr.append_child(self._plan)
        self._plan = sample_opr

    def _visit_orderby(self, orderby_list):
        # orderby_list structure: List[(TupleValueExpression, EnumInt), ...]
        orderby_opr = LogicalOrderBy(orderby_list)
        orderby_opr.append_child(self._plan)
        self._plan = orderby_opr

    def _visit_limit(self, limit_count):
        limit_opr = LogicalLimit(limit_count)
        limit_opr.append_child(self._plan)
        self._plan = limit_opr

    def _visit_union(self, target, all):
        left_child_plan = self._plan
        self.visit_select(target)
        right_child_plan = self._plan
        self._plan = LogicalUnion(all=all)
        self._plan.append_child(left_child_plan)
        self._plan.append_child(right_child_plan)

    def _visit_projection(self, select_columns):
        projection_opr = LogicalProject(select_columns)
        projection_opr.append_child(self._plan)
        self._plan = projection_opr

    def _visit_select_predicate(self, predicate: AbstractExpression):
        filter_opr = LogicalFilter(predicate)
        filter_opr.append_child(self._plan)
        self._plan = filter_opr

    def visit_insert(self, statement: AbstractStatement):
        """Converter for parsed insert statement

        Arguments:
            statement {AbstractStatement} - - [input insert statement]
        """
        '''
        table_ref = statement.table
        table_metainfo = bind_dataset(table_ref.table)
        if table_metainfo is None:
            # Create a new metadata object
            table_metainfo = create_video_metadata(table_ref.table.table_name)

        # populate self._column_map
        self._populate_column_map(table_metainfo)

        # Bind column_list
        bind_columns_expr(statement.column_list, self._column_map)

        # Nothing to be done for values as we add support for other variants of
        # insert we will handle them
        value_list = statement.value_list

        # Ready to create Logical node
        insert_opr = LogicalInsert(
            table_ref, table_metainfo, statement.column_list, value_list)
        self._plan = insert_opr
        '''

    def visit_create(self, statement: AbstractStatement):
        """Convertor for parsed insert Statement

        Arguments:
            statement {AbstractStatement} - - [Create statement]
        """
        table_ref = statement.table_ref
        if table_ref is None:
            logger.error("Missing Table Name In Create Statement")

        create_opr = LogicalCreate(
            table_ref, statement.column_list, statement.if_not_exists)
        self._plan = create_opr

    def visit_drop(self, statement: DropTableStatement):
        drop_opr = LogicalDrop(statement.table_refs, statement.if_exists)
        self._plan = drop_opr

    def visit_create_udf(self, statement: CreateUDFStatement):
        """Convertor for parsed create udf statement

        Arguments:
            statement {CreateUDFStatement} - - Create UDF Statement
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
        Arguments:
            statement(LoadDataStatement): [Load data statement]
        """
        table_metainfo = statement.table_ref.table.table_obj
        load_data_opr = LogicalLoadData(table_metainfo,
                                        statement.path,
                                        statement.column_list,
                                        statement.file_options)
        self._plan = load_data_opr

    def visit_upload(self, statement: UploadStatement):
        """Convertor for parsed upload statement
        Arguments:
            statement(UploadStatement): [Upload statement]
        """
        table_metainfo = statement.table_ref.table.table_obj
        upload_opr = LogicalUpload(statement.path,
                                   statement.video_blob,
                                   table_metainfo,
                                   statement.column_list,
                                   statement.file_options)
        self._plan = upload_opr

    def visit_materialized_view(self,
                                statement: CreateMaterializedViewStatement):
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
            statement {AbstractStatement} - - [Input statement]
        """
        if isinstance(statement, SelectStatement):
            self.visit_select(statement)
        elif isinstance(statement, InsertTableStatement):
            self.visit_insert(statement)
        elif isinstance(statement, CreateTableStatement):
            self.visit_create(statement)
        elif isinstance(statement, DropTableStatement):
            self.visit_drop(statement)
        elif isinstance(statement, CreateUDFStatement):
            self.visit_create_udf(statement)
        elif isinstance(statement, LoadDataStatement):
            self.visit_load_data(statement)
        elif isinstance(statement, UploadStatement):
            self.visit_upload(statement)
        elif isinstance(statement, CreateMaterializedViewStatement):
            self.visit_materialized_view(statement)
        return self._plan

    @property
    def plan(self):
        return self._plan
