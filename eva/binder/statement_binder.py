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

from eva.binder.binder_utils import (
    BinderError,
    bind_table_info,
    check_column_name_is_string,
    check_groupby_pattern,
    check_table_object_is_video,
    extend_star,
    resolve_alias_table_value_expression,
)
from eva.binder.statement_binder_context import StatementBinderContext
from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import IndexType, NdArrayType, TableType, VideoColumnName
from eva.expression.abstract_expression import AbstractExpression, ExpressionType
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.create_index_statement import CreateIndexStatement
from eva.parser.create_mat_view_statement import CreateMaterializedViewStatement
from eva.parser.delete_statement import DeleteTableStatement
from eva.parser.explain_statement import ExplainStatement
from eva.parser.rename_statement import RenameTableStatement
from eva.parser.select_statement import SelectStatement
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
from eva.third_party.huggingface.binder import assign_hf_udf
from eva.utils.generic_utils import get_file_checksum, load_udf_class_from_file
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

    @bind.register(CreateIndexStatement)
    def _bind_create_index_statement(self, node: CreateIndexStatement):
        self.bind(node.table_ref)
        if node.udf_func:
            self.bind(node.udf_func)

        # TODO: create index currently only supports single numpy column.
        assert len(node.col_list) == 1, "Index cannot be created on more than 1 column"

        # TODO: create index currently only works on TableInfo, but will extend later.
        assert node.table_ref.is_table_atom(), "Index can only be created on Tableinfo"

        assert IndexType.is_faiss_index_type(
            node.index_type
        ), "Index type {} is not supported.".format(node.index_type)

        if not node.udf_func:
            # Feature table type needs to be float32 numpy array.
            col_def = node.col_list[0]
            table_ref_obj = node.table_ref.table.table_obj
            col = [col for col in table_ref_obj.columns if col.name == col_def.name][0]
            assert (
                col.array_type == NdArrayType.FLOAT32
            ), "Index input needs to be float32."
            assert len(col.array_dimensions) == 2
        else:
            # Output of the UDF should be 2 dimension and float32 type.
            catalog_manager = CatalogManager()
            udf_obj = catalog_manager.get_udf_catalog_entry_by_name(node.udf_func.name)
            for output in udf_obj.outputs:
                assert (
                    output.array_type == NdArrayType.FLOAT32
                ), "Index input needs to be float32."
                assert (
                    len(output.array_dimensions) == 2
                ), "Index input needs to be 2 dimensional."

    @bind.register(SelectStatement)
    def _bind_select_statement(self, node: SelectStatement):
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

    @bind.register(CreateMaterializedViewStatement)
    def _bind_create_mat_statement(self, node: CreateMaterializedViewStatement):
        self.bind(node.query)
        # Todo Verify if the number projected columns matches table

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
                col_alias = "{}.{}".format(func_expr.alias.alias_name, alias)
                alias_obj = TupleValueExpression(
                    col_name=alias,
                    table_alias=func_expr.alias.alias_name,
                    col_object=obj,
                    col_alias=col_alias,
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
        node.table_alias = table_alias
        if node.col_name == VideoColumnName.audio:
            self._binder_context.enable_audio_retrieval()
        if node.col_name == VideoColumnName.data:
            self._binder_context.enable_video_retrieval()
        node.col_alias = "{}.{}".format(table_alias, node.col_name.lower())
        node.col_object = col_obj

    @bind.register(FunctionExpression)
    def _bind_func_expr(self, node: FunctionExpression):
        # bind all the children
        for child in node.children:
            self.bind(child)

        udf_obj = self._catalog.get_udf_catalog_entry_by_name(node.name)
        if udf_obj is None:
            err_msg = (
                f"UDF with name {node.name} does not exist in the catalog. "
                "Please create the UDF using CREATE UDF command."
            )
            logger.error(err_msg)
            raise BinderError(err_msg)

        if udf_obj.type == "HuggingFace":
            node.function = assign_hf_udf(udf_obj)
        else:
            # Verify the consistency of the UDF. If the checksum of the UDF does not match
            # the one stored in the catalog, an error will be thrown and the user will be
            # asked to register the UDF again.
            assert (
                get_file_checksum(udf_obj.impl_file_path) == udf_obj.checksum
            ), f"""UDF file {udf_obj.impl_file_path} has been modified from the
                registration. Please create a new UDF using the CREATE UDF command or UPDATE the existing one."""

            try:
                node.function = load_udf_class_from_file(
                    udf_obj.impl_file_path, udf_obj.name
                )
            except Exception as e:
                err_msg = (
                    f"{str(e)}. Please verify that the UDF class name in the"
                    "implementation file matches the UDF name."
                )
                logger.error(err_msg)
                raise BinderError(err_msg)

        node.udf_obj = udf_obj
        output_objs = self._catalog.get_udf_io_catalog_output_entries(udf_obj)
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

        resolve_alias_table_value_expression(node)
