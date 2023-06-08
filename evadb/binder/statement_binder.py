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
from pathlib import Path
from typing import Callable

from evadb.binder.binder_utils import (
    BinderError,
    bind_table_info,
    check_column_name_is_string,
    check_groupby_pattern,
    check_table_object_is_groupable,
    extend_star,
    handle_bind_extract_object_function,
    resolve_alias_table_value_expression,
)
from evadb.binder.statement_binder_context import StatementBinderContext
from evadb.catalog.catalog_type import NdArrayType, TableType, VideoColumnName
from evadb.catalog.catalog_utils import get_metadata_properties
from evadb.configuration.constants import EvaDB_INSTALLATION_DIR
from evadb.expression.abstract_expression import AbstractExpression, ExpressionType
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.create_index_statement import CreateIndexStatement
from evadb.parser.create_mat_view_statement import CreateMaterializedViewStatement
from evadb.parser.create_statement import ColumnDefinition, CreateTableStatement
from evadb.parser.delete_statement import DeleteTableStatement
from evadb.parser.explain_statement import ExplainStatement
from evadb.parser.rename_statement import RenameTableStatement
from evadb.parser.select_statement import SelectStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableRef
from evadb.parser.types import UDFType
from evadb.third_party.huggingface.binder import assign_hf_udf
from evadb.utils.generic_utils import get_file_checksum, load_udf_class_from_file
from evadb.utils.logging_manager import logger


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

    @bind.register(CreateIndexStatement)
    def _bind_create_index_statement(self, node: CreateIndexStatement):
        self.bind(node.table_ref)
        if node.udf_func:
            self.bind(node.udf_func)

        # TODO: create index currently only supports single numpy column.
        assert len(node.col_list) == 1, "Index cannot be created on more than 1 column"

        # TODO: create index currently only works on TableInfo, but will extend later.
        assert node.table_ref.is_table_atom(), "Index can only be created on Tableinfo"

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
            udf_obj = self._catalog().get_udf_catalog_entry_by_name(node.udf_func.name)
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
        if node.query is not None:
            self.bind(node.query)
            num_projected_columns = 0
            for expr in node.query.target_list:
                if expr.etype == ExpressionType.TUPLE_VALUE:
                    num_projected_columns += 1
                elif expr.etype == ExpressionType.FUNCTION_EXPRESSION:
                    num_projected_columns += len(expr.output_objs)
                else:
                    raise BinderError(
                        "Unsupported expression type {}.".format(expr.etype)
                    )

            binded_col_list = []
            idx = 0
            for expr in node.query.target_list:
                output_objs = (
                    [(expr.col_name, expr.col_object)]
                    if expr.etype == ExpressionType.TUPLE_VALUE
                    else zip(expr.projection_columns, expr.output_objs)
                )
                for col_name, output_obj in output_objs:
                    binded_col_list.append(
                        ColumnDefinition(
                            col_name,
                            output_obj.type,
                            output_obj.array_type,
                            output_obj.array_dimensions,
                        )
                    )
                    idx += 1
            node.column_list = binded_col_list

    @bind.register(CreateMaterializedViewStatement)
    def _bind_create_mat_statement(self, node: CreateMaterializedViewStatement):
        self.bind(node.query)
        num_projected_columns = 0
        # TODO we should fix the binder. All binded object should have the same interface.
        for expr in node.query.target_list:
            if expr.etype == ExpressionType.TUPLE_VALUE:
                num_projected_columns += 1
            elif expr.etype == ExpressionType.FUNCTION_EXPRESSION:
                num_projected_columns += len(expr.output_objs)
            else:
                raise BinderError("Unsupported expression type {}.".format(expr.etype))

        assert (
            len(node.col_list) == 0 or len(node.col_list) == num_projected_columns
        ), "Projected columns mismatch, expected {} found {}.".format(
            len(node.col_list), num_projected_columns
        )
        binded_col_list = []
        idx = 0
        for expr in node.query.target_list:
            output_objs = (
                [(expr.col_name, expr.col_object)]
                if expr.etype == ExpressionType.TUPLE_VALUE
                else zip(expr.projection_columns, expr.output_objs)
            )
            for col_name, output_obj in output_objs:
                binded_col_list.append(
                    ColumnDefinition(
                        col_name
                        if len(node.col_list) == 0
                        else node.col_list[idx].name,
                        output_obj.type,
                        output_obj.array_type,
                        output_obj.array_dimensions,
                    )
                )
                idx += 1
        node.col_list = binded_col_list

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
        # handle the special case of "extract_object"
        if node.name.upper() == str(UDFType.EXTRACT_OBJECT):
            handle_bind_extract_object_function(node, self)
            return
        # bind all the children
        for child in node.children:
            self.bind(child)

        udf_obj = self._catalog().get_udf_catalog_entry_by_name(node.name)
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
            if udf_obj.type == "ultralytics":
                # manually set the impl_path for yolo udfs we only handle object
                # detection for now, hopefully this can be generalized
                udf_dir = Path(EvaDB_INSTALLATION_DIR) / "udfs"
                udf_obj.impl_file_path = (
                    Path(f"{udf_dir}/yolo_object_detector.py").absolute().as_posix()
                )

            # Verify the consistency of the UDF. If the checksum of the UDF does not
            # match the one stored in the catalog, an error will be thrown and the user
            # will be asked to register the UDF again.
            assert (
                get_file_checksum(udf_obj.impl_file_path) == udf_obj.checksum
            ), f"""UDF file {udf_obj.impl_file_path} has been modified from the
                registration. Please use DROP UDF to drop it and re-create it using CREATE UDF."""

            try:
                udf_class = load_udf_class_from_file(
                    udf_obj.impl_file_path,
                    udf_obj.name,
                )
                # certain udfs take additional inputs like yolo needs the model_name
                # these arguments are passed by the user as part of metadata
                node.function = lambda: udf_class(**get_metadata_properties(udf_obj))
            except Exception as e:
                err_msg = (
                    f"{str(e)}. Please verify that the UDF class name in the"
                    "implementation file matches the UDF name."
                )
                logger.error(err_msg)
                raise BinderError(err_msg)

        node.udf_obj = udf_obj
        output_objs = self._catalog().get_udf_io_catalog_output_entries(udf_obj)
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
