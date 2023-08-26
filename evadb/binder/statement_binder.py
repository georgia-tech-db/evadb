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
    drop_row_id_from_target_list,
    extend_star,
    get_column_definition_from_select_target_list,
    handle_bind_extract_object_function,
    resolve_alias_table_value_expression,
)
from evadb.binder.statement_binder_context import StatementBinderContext
from evadb.catalog.catalog_type import NdArrayType, TableType, VideoColumnName
from evadb.catalog.catalog_utils import get_metadata_properties, is_document_table
from evadb.configuration.constants import EvaDB_INSTALLATION_DIR
from evadb.expression.abstract_expression import AbstractExpression, ExpressionType
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.create_index_statement import CreateIndexStatement
from evadb.parser.create_statement import CreateTableStatement
from evadb.parser.create_udf_statement import CreateUDFStatement
from evadb.parser.delete_statement import DeleteTableStatement
from evadb.parser.explain_statement import ExplainStatement
from evadb.parser.rename_statement import RenameTableStatement
from evadb.parser.select_statement import SelectStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableRef
from evadb.parser.types import UDFType
from evadb.third_party.huggingface.binder import assign_hf_udf
from evadb.utils.generic_utils import load_udf_class_from_file
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

    @bind.register(CreateUDFStatement)
    def _bind_create_udf_statement(self, node: CreateUDFStatement):
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
            assert (
                "predict" in arg_map
            ), f"Creating {node.udf_type} UDFs expects 'predict' metadata."
            # We only support a single predict column for now
            predict_columns = set([arg_map["predict"]])
            inputs, outputs = [], []
            for column in all_column_list:
                if column.name in predict_columns:
                    column.name = column.name + "_predictions"
                    outputs.append(column)
                else:
                    inputs.append(column)
            assert (
                len(node.inputs) == 0 and len(node.outputs) == 0
            ), f"{node.udf_type} UDFs' input and output are auto assigned"
            node.inputs, node.outputs = inputs, outputs

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
            assert (
                len(node.col_list) == 1
            ), f"Index can be only created on one column, but instead {len(node.col_list)} are provided"
            col_def = node.col_list[0]

            table_ref_obj = node.table_ref.table.table_obj
            col_list = [
                col for col in table_ref_obj.columns if col.name == col_def.name
            ]
            assert (
                len(col_list) == 1
            ), f"Index is created on non-existent column {col_def.name}"

            col = col_list[0]
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
                and node.target_list[0].name == "*"
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

        # chunk_params only supported for DOCUMENT TYPE
        if node.from_table.chunk_params:
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
        if node.query is not None:
            self.bind(node.query)

            node.column_list = get_column_definition_from_select_target_list(
                node.query.target_list
            )

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
            output_cols = []
            for obj, alias in zip(func_expr.output_objs, func_expr.alias.col_names):
                col_alias = "{}.{}".format(func_expr.alias.alias_name, alias)
                alias_obj = TupleValueExpression(
                    name=alias,
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
            node.name, node.table_alias
        )
        node.table_alias = table_alias
        if node.name == VideoColumnName.audio:
            self._binder_context.enable_audio_retrieval()
        if node.name == VideoColumnName.data:
            self._binder_context.enable_video_retrieval()
        node.col_alias = "{}.{}".format(table_alias, node.name.lower())
        node.col_object = col_obj

    @bind.register(FunctionExpression)
    def _bind_func_expr(self, node: FunctionExpression):
        # handle the special case of "extract_object"
        if node.name.upper() == str(UDFType.EXTRACT_OBJECT):
            handle_bind_extract_object_function(node, self)
            return

        # Handle Func(*)
        if (
            len(node.children) == 1
            and isinstance(node.children[0], TupleValueExpression)
            and node.children[0].name == "*"
        ):
            node.children = extend_star(self._binder_context)
        # bind all the children
        for child in node.children:
            self.bind(child)

        udf_obj = self._catalog().get_udf_catalog_entry_by_name(node.name)
        if udf_obj is None:
            err_msg = (
                f"Function '{node.name}' does not exist in the catalog. "
                "Please create the function using CREATE UDF command."
            )
            logger.error(err_msg)
            raise BinderError(err_msg)

        if udf_obj.type == "HuggingFace":
            node.function = assign_hf_udf(udf_obj)

        elif udf_obj.type == "Ludwig":
            udf_class = load_udf_class_from_file(
                udf_obj.impl_file_path,
                "GenericLudwigModel",
            )
            udf_metadata = get_metadata_properties(udf_obj)
            assert "model_path" in udf_metadata, "Ludwig models expect 'model_path'."
            node.function = lambda: udf_class(model_path=udf_metadata["model_path"])

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
            # assert (
            #     get_file_checksum(udf_obj.impl_file_path) == udf_obj.checksum
            # ), f"""UDF file {udf_obj.impl_file_path} has been modified from the
            #     registration. Please use DROP UDF to drop it and re-create it # using CREATE UDF."""

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
                    f"{str(e)}. Please verify that the UDF class name in the "
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
