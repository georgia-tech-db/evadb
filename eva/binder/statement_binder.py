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
import sys
from eva.binder.statement_binder_context import StatementBinderContext
from eva.binder.binder_utils import bind_table_info, create_video_metadata, \
    extend_star_in_target_list
from eva.catalog.catalog_manager import CatalogManager
from eva.expression.abstract_expression import AbstractExpression
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.create_mat_view_statement import \
    CreateMaterializedViewStatement
from eva.parser.load_statement import LoadDataStatement
from eva.parser.select_statement import SelectStatement
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
from eva.parser.types import FileFormatType
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
        raise NotImplementedError(f'Cannot bind {type(node)}')

    @bind.register(AbstractStatement)
    def _bind_abstract_statement(self, node: AbstractStatement):
        pass

    @bind.register(AbstractExpression)
    def _bind_abstract_expr(self, node: AbstractExpression):
        for child in node.children:
            self.bind(child)

    @bind.register(SelectStatement)
    def _bind_select_statement(self, node: SelectStatement):
        self.bind(node.from_table)
        if node.where_clause:
            self.bind(node.where_clause)
        if node.target_list:
            # SELECT * support
            if len(node.target_list) == 1 and \
                    isinstance(node.target_list[0], TupleValueExpression) and \
                    node.target_list[0].col_name == '*':
                node.target_list = extend_star_in_target_list(
                    node.from_table.alias, self._binder_context
                )
            for expr in node.target_list:
                self.bind(expr)
        if node.orderby_list:
            for expr in node.orderby_list:
                self.bind(expr[0])
        if node.union_link:
            current_context = self._binder_context
            self._binder_context = StatementBinderContext()
            self.bind(node.union_link)
            self._binder_context = current_context

    @bind.register(CreateMaterializedViewStatement)
    def _bind_create_mat_statement(self,
                                   node: CreateMaterializedViewStatement):
        self.bind(node.query)
        # Todo Verify if the number projected columns matches table

    @bind.register(LoadDataStatement)
    def _bind_load_data_statement(self, node: LoadDataStatement):
        table_ref = node.table_ref
        if node.file_options['file_format'] == FileFormatType.VIDEO:
            # Create a new metadata object
            create_video_metadata(table_ref.table.table_name)

        self.bind(table_ref)

        table_ref_obj = table_ref.table.table_obj
        if table_ref_obj is None:
            error = '{} does not exists. Create the table using \
                            CREATE TABLE.'.format(table_ref.table.table_name)
            logger.error(error)
            raise RuntimeError(error)

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
                        col_object=column))

        # bind the columns
        for expr in column_list:
            self.bind(expr)

        node.column_list = column_list

    @bind.register(TableRef)
    def _bind_tableref(self, node: TableRef):
        if node.is_table_atom():
            # Table
            self._binder_context.add_table_alias(
                node.alias, node.table.table_name)
            bind_table_info(node.table)
        elif node.is_select():
            current_context = self._binder_context
            self._binder_context = StatementBinderContext()
            self.bind(node.select_statement)
            self._binder_context = current_context
            self._binder_context.add_derived_table_alias(
                node.alias, node.select_statement.target_list)
        elif node.is_join():
            self.bind(node.join_node.left)
            self.bind(node.join_node.right)
            if node.join_node.predicate:
                self.bind(node.join_node.predicate)
        elif node.is_func_expr():
            self.bind(node.func_expr)
        else:
            raise ValueError(f'Unsupported node {type(node)}')

    @bind.register(TupleValueExpression)
    def _bind_tuple_expr(self, node: TupleValueExpression):
        table_alias, col_obj = self._binder_context.get_binded_column(
            node.col_name, node.table_alias)
        node.col_alias = '{}.{}'.format(table_alias, node.col_name.lower())
        node.col_object = col_obj

    @bind.register(FunctionExpression)
    def _bind_func_expr(self, node: FunctionExpression):
        # bind all the children
        for child in node.children:
            self.bind(child)

        node.alias = node.alias or node.name.lower()
        udf_obj = self._catalog.get_udf_by_name(node.name)
        assert udf_obj is not None, (
            'UDF with name {} does not exist in the catalog. Please '
            'create the UDF using CREATE UDF command'.format(node.name))

        output_objs = self._catalog.get_udf_outputs(udf_obj)
        if node.output:
            for obj in output_objs:
                if obj.name.lower() == node.output:
                    node.output_col_aliases.append(
                        '{}.{}'.format(node.alias, obj.name.lower()))
                    node.output_objs = [obj]
            assert len(node.output_col_aliases) == 1, (
                'Duplicate columns {} in UDF {}'.format(node.output,
                                                        udf_obj.name))
        else:
            node.output_col_aliases = ['{}.{}'.format(
                node.alias, obj.name.lower()) for obj in output_objs]
            node.output_objs = output_objs

        node.function = path_to_class(
            udf_obj.impl_file_path, udf_obj.name)()
