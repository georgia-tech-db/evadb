# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from functools import singledispatchmethod
from typing import Callable

from evadb.binder.binder_utils import (
    BinderError,
    bind_table_info,
    check_column_name_is_string,
    check_groupby_pattern,
    check_table_object_is_groupable,
    drop_row_id_from_target_list,
    extend_star,
    get_bound_func_expr_outputs_as_tuple_value_expr,
    get_column_definition_from_select_target_list,
)
from evadb.binder.statement_binder_context import StatementBinderContext
from evadb.catalog.catalog_type import ColumnType, TableType
from evadb.catalog.catalog_utils import is_document_table
from evadb.catalog.sql_config import RESTRICTED_COL_NAMES
from evadb.expression.abstract_expression import AbstractExpression, ExpressionType
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.create_function_statement import CreateFunctionStatement
from evadb.parser.create_index_statement import CreateIndexStatement
from evadb.parser.create_statement import ColumnDefinition, CreateTableStatement
from evadb.parser.delete_statement import DeleteTableStatement
from evadb.parser.explain_statement import ExplainStatement
from evadb.parser.rename_statement import RenameTableStatement
from evadb.parser.select_statement import SelectStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableRef
from evadb.utils.generic_utils import string_comparison_case_insensitive


class StatementBinder:
    def __init__(self, binder_context: StatementBinderContext):
        self._binder_context = binder_context
        self._catalog: Callable = binder_context._catalog

    @singledispatchmethod
    def bind(self, node):
        raise NotImplementedError(f"Cannot bind {type(node)}")

    @bind.register(AbstractStatement)
    def _bind_abstract_statement(self, node: AbstractStatement):
        pass

    @bind.register(AbstractExpression)
    def _bind_abstract_expr(self, node: AbstractExpression):
        for child in node.children:
            self.bind(child)

    @bind.register(ExplainStatement)
    def _bind_explain_statement(self, node: ExplainStatement):
        self.bind(node.explainable_stmt)

    @bind.register(CreateFunctionStatement)
    def _bind_create_function_statement(self, node: CreateFunctionStatement):
        if node.query is not None:
            self.bind(node.query)
            # Drop the automatically generated _row_id column
            node.query.target_list = drop_row_id_from_target_list(
                node.query.target_list
            )
            all_column_list = get_column_definition_from_select_target_list(
                node.query.target_list
            )
            arg_map = {key: value for key, value in node.metadata}
            inputs, outputs = [], []
            if string_comparison_case_insensitive(node.function_type, "ludwig"):
                assert (
                    "predict" in arg_map
                ), f"Creating {node.function_type} functions expects 'predict' metadata."
                # We only support a single predict column for now
                predict_columns = set([arg_map["predict"]])
                for column in all_column_list:
                    if column.name in predict_columns:
                        column.name = column.name + "_predictions"

                        outputs.append(column)
                    else:
                        inputs.append(column)
            elif string_comparison_case_insensitive(
                node.function_type, "sklearn"
            ) or string_comparison_case_insensitive(node.function_type, "XGBoost"):
                assert (
                    "predict" in arg_map
                ), f"Creating {node.function_type} functions expects 'predict' metadata."
                # We only support a single predict column for now
                predict_columns = set([arg_map["predict"]])
                for column in all_column_list:
                    if column.name in predict_columns:
                        outputs.append(column)
                    else:
                        inputs.append(column)
            elif string_comparison_case_insensitive(node.function_type, "forecasting"):
                # Forecasting models have only one input column which is horizon
                inputs = [ColumnDefinition("horizon", ColumnType.INTEGER, None, None)]
                # Currently, we only support univariate forecast which should have three output columns, unique_id, ds, and y.
                # The y column is required. unique_id and ds will be auto generated if not found.
                required_columns = set([arg_map.get("predict", "y")])
                for column in all_column_list:
                    if column.name == arg_map.get("id", "unique_id"):
                        outputs.append(column)
                    elif column.name == arg_map.get("time", "ds"):
                        outputs.append(column)
                    elif column.name == arg_map.get("predict", "y"):
                        outputs.append(column)
                        required_columns.remove(column.name)
                assert (
                    len(required_columns) == 0
                ), f"Missing required {required_columns} columns for forecasting function."
                outputs.extend(
                    [
                        ColumnDefinition(
                            arg_map.get("predict", "y") + "-lo",
                            ColumnType.FLOAT,
                            None,
                            None,
                        ),
                        ColumnDefinition(
                            arg_map.get("predict", "y") + "-hi",
                            ColumnType.FLOAT,
                            None,
                            None,
                        ),
                    ]
                )
            else:
                raise BinderError(
                    f"Unsupported type of function: {node.function_type}."
                )
            assert (
                len(node.inputs) == 0 and len(node.outputs) == 0
            ), f"{node.function_type} functions' input and output are auto assigned"
            node.inputs, node.outputs = inputs, outputs

    @bind.register(SelectStatement)
    def _bind_select_statement(self, node: SelectStatement):
        if node.from_table:
            self.bind(node.from_table)

        if node.where_clause:
            self.bind(node.where_clause)
            if node.where_clause.etype == ExpressionType.COMPARE_LIKE:
                check_column_name_is_string(node.where_clause.children[0])

        if node.target_list:
            # SELECT * support
            if (
                len(node.target_list) == 1
                and isinstance(node.target_list[0], TupleValueExpression)
                and node.target_list[0].name == "*"
            ):
                node.target_list = extend_star(self._binder_context)
            for expr in node.target_list:
                self.bind(expr)
                if isinstance(expr, FunctionExpression):
                    output_cols = get_bound_func_expr_outputs_as_tuple_value_expr(expr)
                    self._binder_context.add_derived_table_alias(
                        expr.alias.alias_name, output_cols
                    )

        if node.groupby_clause:
            self.bind(node.groupby_clause)
            check_table_object_is_groupable(node.from_table)
            check_groupby_pattern(node.from_table, node.groupby_clause.value)
        if node.orderby_list:
            for expr in node.orderby_list:
                self.bind(expr[0])
        if node.union_link:
            current_context = self._binder_context
            self._binder_context = StatementBinderContext(self._catalog)
            self.bind(node.union_link)
            self._binder_context = current_context

        # chunk_params only supported for DOCUMENT TYPE
        if node.from_table and node.from_table.chunk_params:
            assert is_document_table(
                node.from_table.table.table_obj
            ), "CHUNK related parameters only supported for DOCUMENT tables."

        assert not (
            self._binder_context.is_retrieve_audio()
            and self._binder_context.is_retrieve_video()
        ), "Cannot query over both audio and video streams"

        if self._binder_context.is_retrieve_audio():
            node.from_table.get_audio = True
        if self._binder_context.is_retrieve_video():
            node.from_table.get_video = True

    @bind.register(DeleteTableStatement)
    def _bind_delete_statement(self, node: DeleteTableStatement):
        self.bind(node.table_ref)
        if node.where_clause:
            self.bind(node.where_clause)

    @bind.register(CreateTableStatement)
    def _bind_create_statement(self, node: CreateTableStatement):
        # we don't allow certain keywords in the column_names
        for col in node.column_list:
            assert (
                col.name.lower() not in RESTRICTED_COL_NAMES
            ), f"EvaDB does not allow to create a table with column name {col.name}"

        if node.query is not None:
            self.bind(node.query)

            node.column_list = get_column_definition_from_select_target_list(
                node.query.target_list
            )

            # verify if the table to be created is valid.
            # possible issues: the native database does not exists.

    @bind.register(CreateIndexStatement)
    def _bind_create_index_statement(self, node: CreateIndexStatement):
        from evadb.binder.create_index_statement_binder import bind_create_index

        bind_create_index(self, node)

    @bind.register(RenameTableStatement)
    def _bind_rename_table_statement(self, node: RenameTableStatement):
        self.bind(node.old_table_ref)
        assert (
            node.old_table_ref.table.table_obj.table_type != TableType.STRUCTURED_DATA
        ), "Rename not yet supported on structured data"

    @bind.register(TableRef)
    def _bind_tableref(self, node: TableRef):
        if node.is_table_atom():
            # Table
            self._binder_context.add_table_alias(
                node.alias.alias_name, node.table.database_name, node.table.table_name
            )
            bind_table_info(self._catalog(), node.table)
        elif node.is_select():
            current_context = self._binder_context
            self._binder_context = StatementBinderContext(self._catalog)
            self.bind(node.select_statement)
            self._binder_context = current_context
            self._binder_context.add_derived_table_alias(
                node.alias.alias_name, node.select_statement.target_list
            )
        elif node.is_join():
            self.bind(node.join_node.left)
            self.bind(node.join_node.right)
            if node.join_node.predicate:
                self.bind(node.join_node.predicate)
        elif node.is_table_valued_expr():
            func_expr = node.table_valued_expr.func_expr
            func_expr.alias = node.alias
            self.bind(func_expr)
            output_cols = get_bound_func_expr_outputs_as_tuple_value_expr(func_expr)
            self._binder_context.add_derived_table_alias(
                func_expr.alias.alias_name, output_cols
            )
        else:
            raise BinderError(f"Unsupported node {type(node)}")

    @bind.register(TupleValueExpression)
    def _bind_tuple_expr(self, node: TupleValueExpression):
        from evadb.binder.tuple_value_expression_binder import bind_tuple_expr

        bind_tuple_expr(self, node)

    @bind.register(FunctionExpression)
    def _bind_func_expr(self, node: FunctionExpression):
        from evadb.binder.function_expression_binder import bind_func_expr

        bind_func_expr(self, node)
