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
from pathlib import Path

import pandas as pd

from evadb.catalog.catalog_type import VectorStoreType
from evadb.catalog.sql_config import ROW_NUM_COLUMN
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import ExecutorError, handle_vector_store_params
from evadb.expression.function_expression import FunctionExpression
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.create_index_plan import CreateIndexPlan
from evadb.third_party.databases.interface import get_database_handler
from evadb.third_party.vector_stores.types import FeaturePayload
from evadb.third_party.vector_stores.utils import VectorStoreFactory
from evadb.utils.logging_manager import logger


class CreateIndexExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: CreateIndexPlan):
        super().__init__(db, node)

        self.name = self.node.name
        self.if_not_exists = self.node.if_not_exists
        self.table_ref = self.node.table_ref
        self.col_list = self.node.col_list
        self.vector_store_type = self.node.vector_store_type
        self.project_expr_list = self.node.project_expr_list
        self.index_def = self.node.index_def

    def exec(self, *args, **kwargs):
        # Vector type specific creation.
        if self.vector_store_type == VectorStoreType.PGVECTOR:
            self._create_native_index()
        else:
            self._create_evadb_index()

        yield Batch(
            pd.DataFrame([f"Index {self.name} successfully added to the database."])
        )

    # Create index through the native storage engine.
    def _create_native_index(self):
        table = self.table_ref.table
        db_catalog_entry = self.catalog().get_database_catalog_entry(
            table.database_name
        )

        with get_database_handler(
            db_catalog_entry.engine, **db_catalog_entry.params
        ) as handler:
            # As other libraries, we default to HNSW and L2 distance.
            resp = handler.execute_native_query(
                f"""CREATE INDEX {self.name} ON {table.table_name}
                    USING hnsw ({self.col_list[0].name} vector_l2_ops)"""
            )
            if resp.error is not None:
                raise ExecutorError(
                    f"Native engine create index encounters error: {resp.error}"
                )

    # On-disk saving path for EvaDB index.
    def _get_evadb_index_save_path(self) -> Path:
        index_dir = Path(self.config.get_value("storage", "index_dir"))
        if not index_dir.exists():
            index_dir.mkdir(parents=True, exist_ok=True)
        return str(
            index_dir / Path("{}_{}.index".format(self.vector_store_type, self.name))
        )

    # Create EvaDB index.
    def _create_evadb_index(self):
        # Find function expression.
        function_expression, function_expression_signature = None, None
        for project_expr in self.project_expr_list:
            if isinstance(project_expr, FunctionExpression):
                function_expression = project_expr
                function_expression_signature = project_expr.signature()

        # Get feature tables.
        feat_tb_catalog_entry = self.table_ref.table.table_obj

        # Get feature column.
        feat_col_name = self.col_list[0].name
        feat_col_catalog_entry = [
            col for col in feat_tb_catalog_entry.columns if col.name == feat_col_name
        ][0]

        if function_expression is not None:
            feat_col_name = function_expression.output_objs[0].name

        index_catalog_entry = self.catalog().get_index_catalog_entry_by_name(self.name)
        index_path = self._get_evadb_index_save_path()

        if index_catalog_entry is not None:
            msg = f"Index {self.name} already exists."
            if self.if_not_exists:
                if (
                    index_catalog_entry.feat_column == feat_col_catalog_entry
                    and index_catalog_entry.function_signature
                    == function_expression_signature
                    and index_catalog_entry.type == self.node.vector_store_type
                ):
                    # Only update index if everything matches.
                    logger.warn(msg + " It will be updated on existing table.")
                    index = VectorStoreFactory.init_vector_store(
                        self.vector_store_type,
                        self.name,
                        **handle_vector_store_params(
                            self.vector_store_type, index_path
                        ),
                    )
                else:
                    # Skip index update if CREATE INDEX runs on a different index.
                    logger.warn(msg)
                    return
            else:
                logger.error(msg)
                raise ExecutorError(msg)
        else:
            index = None

        try:
            # Add features to index.
            for input_batch in self.children[0].exec():
                input_batch.drop_column_alias()
                feat = input_batch.column_as_numpy_array(feat_col_name)
                row_num = input_batch.column_as_numpy_array(ROW_NUM_COLUMN)

                for i in range(len(input_batch)):
                    row_feat = feat[i].reshape(1, -1)

                    # Create new index if not exists.
                    if index is None:
                        input_dim = row_feat.shape[1]
                        index = VectorStoreFactory.init_vector_store(
                            self.vector_store_type,
                            self.name,
                            **handle_vector_store_params(
                                self.vector_store_type, index_path
                            ),
                        )
                        index.create(input_dim)

                    # Row ID for mapping back to the row.
                    index.add([FeaturePayload(row_num[i], row_feat)])

            # Persist index.
            index.persist()

            # Save to catalog.
            if index_catalog_entry is None:
                self.catalog().insert_index_catalog_entry(
                    self.name,
                    index_path,
                    self.vector_store_type,
                    feat_col_catalog_entry,
                    function_expression_signature,
                    self.index_def,
                )
        except Exception as e:
            # Delete index.
            if index:
                index.delete()

            # Throw exception back to user.
            raise ExecutorError(str(e))
