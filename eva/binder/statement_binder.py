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

from functools import singledispatch
from typing import Union
from eva.binder.statement_binder_context import StatementBinderContext
from eva.catalog.catalog_manager import CatalogManager
from eva.expression.abstract_expression import AbstractExpression
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.create_mat_view_statement import \
    CreateMaterializedViewStatement
from eva.parser.select_statement import SelectStatement

from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
from eva.utils.generic_utils import path_to_class


class StatementBinder:
    def __init__(self, binder_context: StatementBinderContext):
        self._binder_context = binder_context
        self._catalog = CatalogManager()

    def bind_node(self, node: Union[AbstractStatement, AbstractExpression]):

        @singledispatch
        def bind(node: AbstractStatement):
            pass

        @bind.register(AbstractExpression)
        def _(node: AbstractExpression):
            for child in node.children:
                bind(child)

        @bind.register(SelectStatement)
        def _(node: SelectStatement):
            bind(node.from_table)
            if node.where_clause:
                bind(node.where_clause)
            if node.target_list:
                for expr in node.target_list:
                    bind(expr)
            if node.orderby_list:
                for expr in node.orderby_list:
                    bind(expr[0])
            if node.union_link:
                current_context = self._binder_context
                self._binder_context = StatementBinderContext()
                bind(node.union_link)
                self._binder_context = current_context

        @bind.register(CreateMaterializedViewStatement)
        def _(node: CreateMaterializedViewStatement):
            bind(node.query)
            # Todo Verify if the number projected columns matches table

        @bind.register(TableRef)
        def _(node: TableRef):
            if node.is_select():
                current_context = self._binder_context
                self._binder_context = StatementBinderContext()
                bind(node.table)
                self._binder_context = current_context
                self._binder_context.add_derived_table_alias(
                    node.alias, node.table.target_list)
            else:
                # Table
                self._binder_context.add_table_alias(
                    node.alias, node.table.table_name)

        @bind.register(TupleValueExpression)
        def _(node: TupleValueExpression):
            table_alias, col_obj = self._binder_context.get_binded_column(
                node.col_name, node.table_alias)
            node.col_alias = '{}.{}'.format(table_alias, node.col_name.lower())
            node.col_object = col_obj

        @bind.register(FunctionExpression)
        def _(node: FunctionExpression):
            # bind all the children
            for child in node.children:
                bind(child)

            node.alias = node.alias or node.name.lower()
            udf_obj = self._catalog.get_udf_by_name(node.name)
            assert udf_obj is not None, '''UDF with name {} does not
                                           exist in the catalog.
                                           Please create the UDF
                                           using CREATE UDF
                                           command'''.format(
                node.name)

            output_objs = self._catalog.get_udf_outputs(udf_obj)
            if node.output:
                for obj in output_objs:
                    if obj.name.lower() == node.output:
                        node.output_col_aliases.append(
                            '{}.{}'.format(node.alias, obj.name.lower()))
                assert len(node.output_col_aliases) == 1, '''Duplicate
                                                          columns {}
                                                          in UDF
                                                          {}'''.format(
                    node.output, udf_obj.name)
            else:
                node.output_col_aliases = ['{}.{}'.format(
                    node.alias, obj.name) for obj in output_objs]

            node.function = path_to_class(
                udf_obj.impl_file_path, udf_obj.name)()
            node.output_objs = output_objs

        bind(node)
