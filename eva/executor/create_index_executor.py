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
import os
from pathlib import Path

import faiss
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import (
    ColumnType,
    Dimension,
    IndexType,
    NdArrayType,
    TableType,
)
from eva.configuration.constants import EVA_DEFAULT_DIR, INDEX_DIR
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.parser.create_statement import ColConstraintInfo, ColumnDefinition
from eva.planner.create_index_plan import CreateIndexPlan
from eva.sql_config import IDENTIFIER_COLUMN
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


class CreateIndexExecutor(AbstractExecutor):
    def __init__(self, node: CreateIndexPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        catalog_manager = CatalogManager()
        if catalog_manager.get_index_by_name(self.node.name):
            msg = f"Index {self.node.name} already exists."
            logger.error(msg)
            raise ExecutorError(msg)

        try:
            # Get feature tables.
            feat_df_metadata = self.node.table_ref.table.table_obj

            # Add features to index.
            # TODO: batch size is hardcoded for now.
            index = None
            input_dim, num_rows = -1, 0
            logical_to_row_id = dict()
            storage_engine = StorageEngine.factory(feat_df_metadata)
            for batch in storage_engine.read(feat_df_metadata, 1):
                # Feature column name.
                feat_col_name = self.node.col_list[0].name

                # Pandas wraps numpy array as an object inside a numpy
                # array. Use zero index to get the actual numpy array.
                feat = batch.column_as_numpy_array(feat_col_name)[0]
                if index is None:
                    input_dim = feat.shape[-1]
                    index = self._create_index(self.node.index_type, input_dim)
                index.add(feat)

                # Secondary mapping.
                row_id = batch.column_as_numpy_array(IDENTIFIER_COLUMN)[0]
                logical_to_row_id[num_rows] = row_id

                num_rows += 1

            # Get index IO list.
            io_list = self._get_index_io_list(input_dim)

            # Build secondary index maaping.
            secondary_index_df_metadata = self._create_secondary_index_table()
            storage_engine = StorageEngine.factory(secondary_index_df_metadata)
            storage_engine.create(secondary_index_df_metadata)

            # Write mapping.
            logical_id, row_id = list(logical_to_row_id.keys()), list(
                logical_to_row_id.values()
            )
            secondary_index = Batch(
                pd.DataFrame(data={"logical_id": logical_id, "row_id": row_id})
            )
            storage_engine.write(secondary_index_df_metadata, secondary_index)

            # Persist index.
            faiss.write_index(index, self._get_index_save_path())

            # Save to catalog.
            catalog_manager.create_index(
                self.node.name,
                self._get_index_save_path(),
                self.node.index_type,
                io_list,
                secondary_index_df_metadata,
            )

            yield Batch(
                pd.DataFrame(
                    [f"Index {self.node.name} successfully added to the database."]
                )
            )
        except Exception as e:
            # Roll back in reverse order.
            # Delete on-disk index.
            if os.path.exists(self._get_index_save_path()):
                os.remove(self._get_index_save_path())

            # Drop secondary index table.
            secondary_index_tb_name = "secondary_index_{}_{}".format(
                self.node.index_type, self.node.name
            )
            if catalog_manager.check_table_exists(
                None,
                secondary_index_tb_name,
            ):
                secondary_index_metadata = catalog_manager.get_dataset_metadata(
                    None, secondary_index_tb_name
                )
                storage_engine = StorageEngine.factory(secondary_index_metadata)
                storage_engine.drop(secondary_index_metadata)
                catalog_manager.drop_dataset_metadata(
                    None,
                    secondary_index_tb_name,
                )

            # Throw exception back to user.
            raise ExecutorError(str(e))

    def _get_index_save_path(self):
        return str(
            EVA_DEFAULT_DIR
            / INDEX_DIR
            / Path("{}_{}.index".format(self.node.index_type, self.node.name))
        )

    def _get_index_io_list(self, input_dim):
        # Input dimension is inferred from the actual feature.
        catalog_manager = CatalogManager()
        input_index_io = catalog_manager.index_io(
            "input_feature",
            ColumnType.NDARRAY,
            NdArrayType.FLOAT32,
            [Dimension.ANYDIM, input_dim],
            True,
        )

        # Output dimension depends on number of searched
        # feature vectors and top N similar feature vectors.
        # IndexIO has detailed documentation about input and
        # output format of index.
        id_index_io = catalog_manager.index_io(
            "logical_id",
            ColumnType.NDARRAY,
            NdArrayType.INT64,
            [Dimension.ANYDIM, Dimension.ANYDIM],
            False,
        )
        distance_index_io = catalog_manager.index_io(
            "distance",
            ColumnType.NDARRAY,
            NdArrayType.FLOAT32,
            [Dimension.ANYDIM, Dimension.ANYDIM],
            False,
        )

        return [input_index_io, id_index_io, distance_index_io]

    def _create_secondary_index_table(self):
        # Build secondary index to map from index Logical ID to Row ID.
        # Use save_file_path's hash value to retrieve the table.
        catalog_manager = CatalogManager()
        col_list = [
            ColumnDefinition(
                "logical_id",
                ColumnType.INTEGER,
                None,
                [],
                ColConstraintInfo(unique=True),
            ),
            ColumnDefinition(
                "row_id",
                ColumnType.INTEGER,
                None,
                [],
                ColConstraintInfo(unique=True),
            ),
        ]
        col_metadata = [
            catalog_manager.create_column_metadata(
                col.name, col.type, col.array_type, col.dimension, col.cci
            )
            for col in col_list
        ]
        catalog_manager = CatalogManager()
        df_metadata = catalog_manager.create_metadata(
            "secondary_index_{}_{}".format(self.node.index_type, self.node.name),
            str(
                EVA_DEFAULT_DIR
                / INDEX_DIR
                / Path("{}_{}.secindex".format(self.node.index_type, self.node.name))
            ),
            col_metadata,
            identifier_column="logical_id",
            table_type=TableType.STRUCTURED_DATA,
        )
        return df_metadata

    def _create_index(self, index_type: IndexType, input_dim: int):
        if index_type == IndexType.HNSW:
            return faiss.IndexHNSWFlat(input_dim, 32)
        else:
            raise ExecutorError(f"Index Type {index_type} is not supported.")
