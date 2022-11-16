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
import sys
from pathlib import Path
from typing import Union

from eva.binder.binder_utils import (
    BinderError,
    bind_table_info,
    check_groupby_pattern,
    check_table_object_is_video,
    create_video_metadata,
    extend_star,
)
from eva.binder.statement_binder_context import StatementBinderContext
from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.expression.abstract_expression import AbstractExpression
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.alias import Alias
from eva.parser.create_mat_view_statement import CreateMaterializedViewStatement
from eva.parser.drop_statement import DropTableStatement
from eva.parser.explain_statement import ExplainStatement
from eva.parser.load_statement import LoadDataStatement
from eva.parser.select_statement import SelectStatement
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
from eva.parser.types import FileFormatType
from eva.parser.upload_statement import UploadStatement
from eva.utils.generic_utils import path_to_class
from eva.utils.logging_manager import logger

if sys.version_info >= (3, 8):
    from functools import singledispatchmethod
else:
    # https://stackoverflow.com/questions/24601722/how-can-i-use-functools-singledispatch-with-instance-methods
    from functools import singledispatch, update_wrapper

    def singledispatchmethod(func):
        dispatcher = singledispatch(func)

        def wrapper(*args, **kw):
            return dispatcher.dispatch(args[1].__class__)(*args, **kw)

        wrapper.register = dispatcher.register
        update_wrapper(wrapper, func)
        return wrapper


class StatementBinder:
    def __init__(self, binder_context: StatementBinderContext):
        self._binder_context = binder_context
        self._catalog = CatalogManager()

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

    @bind.register(SelectStatement)
    def _bind_select_statement(self, node: SelectStatement):
        self.bind(node.from_table)
        if node.where_clause:
            self.bind(node.where_clause)
        if node.target_list:
            # SELECT * support
            if (
                len(node.target_list) == 1
                and isinstance(node.target_list[0], TupleValueExpression)
                and node.target_list[0].col_name == "*"
            ):
                node.target_list = extend_star(self._binder_context)
            for expr in node.target_list:
                self.bind(expr)
        if node.groupby_clause:
            self.bind(node.groupby_clause)
            check_groupby_pattern(node.groupby_clause.value)
            check_table_object_is_video(node.from_table)
        if node.orderby_list:
            for expr in node.orderby_list:
                self.bind(expr[0])
        if node.union_link:
            current_context = self._binder_context
            self._binder_context = StatementBinderContext()
            self.bind(node.union_link)
            self._binder_context = current_context

    @bind.register(CreateMaterializedViewStatement)
    def _bind_create_mat_statement(self, node: CreateMaterializedViewStatement):
        self.bind(node.query)
        # Todo Verify if the number projected columns matches table

    @bind.register(LoadDataStatement)
    @bind.register(UploadStatement)
    def _bind_load_and_upload_data_statement(
        self, node: Union[LoadDataStatement, UploadStatement]
    ):
        table_ref = node.table_ref
        name = table_ref.table.table_name
        if node.file_options["file_format"] == FileFormatType.VIDEO:
            # Sanity check to make sure there is no existing video table with same name
            if self._catalog.check_table_exists(
                table_ref.table.database_name, table_ref.table.table_name
            ):
                msg = f"Adding to an existing video table {name}."
                logger.info(msg)
            else:

                # create catalog entry only if the file path exists
                upload_dir = Path(
                    ConfigurationManager().get_value("storage", "upload_dir")
                )
                if (
                    Path(node.path).exists()
                    or Path(Path(upload_dir) / node.path).exists()
                ):
                    create_video_metadata(name)

                # else raise error
                else:
                    err_msg = f"Video file {node.path} does not exist."
                    logger.error(err_msg)
                    raise BinderError(err_msg)

        self.bind(table_ref)

        table_ref_obj = table_ref.table.table_obj
        if table_ref_obj is None:
            error = f"{name} does not exist."
            logger.error(error)
            raise BinderError(error)

        # if query had columns specified, we just copy them
        if node.column_list is not None:
            column_list = node.column_list

        # else we curate the column list from the metadata
        else:
            column_list = []
            for column in table_ref_obj.columns:
                column_list.append(
                    TupleValueExpression(
                        col_name=column.name,
                        table_alias=table_ref_obj.name.lower(),
                        col_object=column,
                    )
                )

        # bind the columns
        for expr in column_list:
            self.bind(expr)

        node.column_list = column_list

    @bind.register(DropTableStatement)
    def _bind_drop_table_statement(self, node: DropTableStatement):
        for table in node.table_refs:
            self.bind(table)

    @bind.register(TableRef)
    def _bind_tableref(self, node: TableRef):
        if node.is_table_atom():
            # Table
            self._binder_context.add_table_alias(
                node.alias.alias_name, node.table.table_name
            )
            bind_table_info(node.table)
        elif node.is_select():
            current_context = self._binder_context
            self._binder_context = StatementBinderContext()
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
            output_cols = []
            for obj, alias in zip(func_expr.output_objs, func_expr.alias.col_names):
                alias_obj = self._catalog.udf_io(
                    alias,
                    data_type=obj.type,
                    array_type=obj.array_type,
                    dimensions=obj.array_dimensions,
                    is_input=obj.is_input,
                )

                output_cols.append(alias_obj)
            self._binder_context.add_derived_table_alias(
                func_expr.alias.alias_name, output_cols
            )
        else:
            raise BinderError(f"Unsupported node {type(node)}")

    @bind.register(TupleValueExpression)
    def _bind_tuple_expr(self, node: TupleValueExpression):
        table_alias, col_obj = self._binder_context.get_binded_column(
            node.col_name, node.table_alias
        )
        node.col_alias = "{}.{}".format(table_alias, node.col_name.lower())
        node.col_object = col_obj

    @bind.register(FunctionExpression)
    def _bind_func_expr(self, node: FunctionExpression):
        # bind all the children
        for child in node.children:
            self.bind(child)

        udf_obj = self._catalog.get_udf_by_name(node.name)
        if udf_obj is None:
            err_msg = (
                f"UDF with name {node.name} does not exist in the catalog. "
                "Please create the UDF using CREATE UDF command."
            )
            logger.error(err_msg)
            raise BinderError(err_msg)

        try:
            node.function = path_to_class(udf_obj.impl_file_path, udf_obj.name)
        except Exception as e:
            err_msg = (
                f"{str(e)}. Please verify that the UDF class name in the"
                "implementation file matches the UDF name."
            )
            logger.error(err_msg)
            raise BinderError(err_msg)

        output_objs = self._catalog.get_udf_outputs(udf_obj)
        if node.output:
            for obj in output_objs:
                if obj.name.lower() == node.output:
                    node.output_objs = [obj]
            if not node.output_objs:
                err_msg = f"Output {node.output} does not exist for {udf_obj.name}."
                logger.error(err_msg)
                raise BinderError(err_msg)
            node.projection_columns = [node.output]
        else:
            node.output_objs = output_objs
            node.projection_columns = [obj.name.lower() for obj in output_objs]

        default_alias_name = node.name.lower()
        default_output_col_aliases = [str(obj.name.lower()) for obj in node.output_objs]
        if not node.alias:
            node.alias = Alias(default_alias_name, default_output_col_aliases)
        else:
            if not len(node.alias.col_names):
                node.alias = Alias(node.alias.alias_name, default_output_col_aliases)
            else:
                output_aliases = [
                    str(col_name.lower()) for col_name in node.alias.col_names
                ]
                node.alias = Alias(node.alias.alias_name, output_aliases)

        if len(node.alias.col_names) != len(node.output_objs):
            err_msg = (
                f"Expected {len(node.output_objs)} output columns for "
                f"{node.alias.alias_name}, got {len(node.alias.col_names)}."
            )
            logger.error(err_msg)
            raise BinderError(err_msg)
