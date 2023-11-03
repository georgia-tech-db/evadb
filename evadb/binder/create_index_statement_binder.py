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
from evadb.binder.binder_utils import BinderError, create_row_num_tv_expr
from evadb.binder.statement_binder import StatementBinder
from evadb.catalog.catalog_type import NdArrayType, VectorStoreType
from evadb.expression.function_expression import FunctionExpression
from evadb.parser.create_index_statement import CreateIndexStatement
from evadb.third_party.databases.interface import get_database_handler


def bind_create_index(binder: StatementBinder, node: CreateIndexStatement):
    binder.bind(node.table_ref)

    # Bind all projection expressions.
    func_project_expr = None
    for project_expr in node.project_expr_list:
        binder.bind(project_expr)
        if isinstance(project_expr, FunctionExpression):
            func_project_expr = project_expr

    # Append ROW_NUM_COLUMN.
    node.project_expr_list += [create_row_num_tv_expr(node.table_ref.alias)]

    # TODO: create index currently only supports single numpy column.
    assert len(node.col_list) == 1, "Index cannot be created on more than 1 column"

    # TODO: create index currently only works on TableInfo, but will extend later.
    assert (
        node.table_ref.is_table_atom()
    ), "Index can only be created on an existing table"

    # Vector type specific check.
    catalog = binder._catalog()
    if node.vector_store_type == VectorStoreType.PGVECTOR:
        db_catalog_entry = catalog.get_database_catalog_entry(
            node.table_ref.table.database_name
        )
        if db_catalog_entry.engine != "postgres":
            raise BinderError("PGVECTOR index works only with Postgres data source.")
        with get_database_handler(
            db_catalog_entry.engine, **db_catalog_entry.params
        ) as handler:
            # Check if vector extension is enabled, which is required for PGVECTOR.
            df = handler.execute_native_query(
                "SELECT * FROM pg_extension WHERE extname = 'vector'"
            ).data
            if len(df) == 0:
                raise BinderError("PGVECTOR extension is not enabled.")

        # Skip the rest of checking, because it will be anyway taken care by the
        # underlying native storage engine.
        return

    # Index can be only created on single column.
    assert (
        len(node.col_list) == 1
    ), f"Index can be only created on one column, but instead {len(node.col_list)} are provided"
    col_def = node.col_list[0]

    if func_project_expr is None:
        # Feature table type needs to be float32 numpy array.
        table_ref_obj = node.table_ref.table.table_obj
        col_list = [col for col in table_ref_obj.columns if col.name == col_def.name]
        assert (
            len(col_list) == 1
        ), f"Index is created on non-existent column {col_def.name}"

        col = col_list[0]
        assert len(col.array_dimensions) == 2

        # Vector type specific check.
        if node.vector_store_type == VectorStoreType.FAISS:
            assert (
                col.array_type == NdArrayType.FLOAT32
            ), "Index input needs to be float32."
    else:
        # Output of the function should be 2 dimension and float32 type.
        function_obj = binder._catalog().get_function_catalog_entry_by_name(
            func_project_expr.name
        )
        for output in function_obj.outputs:
            assert (
                len(output.array_dimensions) == 2
            ), "Index input needs to be 2 dimensional."

            # Vector type specific check.
            if node.vector_store_type == VectorStoreType.FAISS:
                assert (
                    output.array_type == NdArrayType.FLOAT32
                ), "Index input needs to be float32."
