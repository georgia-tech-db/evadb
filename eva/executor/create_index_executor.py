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
from copy import deepcopy
from pathlib import Path

import faiss
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.column_type import ColumnType, NdArrayType, Dimension
from eva.catalog.index_type import IndexType
from eva.configuration.constants import EVA_DEFAULT_DIR, INDEX_DIR
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.parser.create_statement import ColConstraintInfo, ColumnDefinition
from eva.planner.create_index_plan import CreateIndexPlan
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
            raise RuntimeError(msg)

        # Get feature tables.
        table_ref = self.node.table_ref
        df_metadata = CatalogManager().get_dataset_metadata(
            table_ref.table.database_name, table_ref.table.table_name
        )

        # Add features to index.
        # TODO: batch size is hardcoded for now.
        index = None
        input_dim, feat_size = -1, 0
        for batch in StorageEngine.read(df_metadata, 1):
            feat = batch.column_as_numpy_array(self.node.col_list[0].name)[0]
            if index is None:
                input_dim = feat.shape[-1]
                index = self._create_index(self.node.index_type, input_dim)
            index.add(feat)
            feat_size += 1

        # Input dimension is inferred from the actual feature.
        input_index_io = CatalogManager().index_io(
            "input_feature",
            ColumnType.NDARRAY,
            NdArrayType.FLOAT32,
            [Dimension.ANYDIM, input_dim],
            True,
        )

        # Output dimension can be hardcoded.
        id_index_io = CatalogManager().index_io(
            "logical_id",
            ColumnType.NDARRAY,
            NdArrayType.INT64,
            [Dimension.ANYDIM, 1],
            False,
        )
        distance_index_io = CatalogManager().index_io(
            "distance",
            ColumnType.NDARRAY,
            NdArrayType.FLOAT32,
            [Dimension.ANYDIM, 1],
            False,
        )
        save_file_path = (
            EVA_DEFAULT_DIR
            / INDEX_DIR
            / Path("{}_{}.index".format(self.node.index_type, self.node.name))
        )

        io_list = [input_index_io, id_index_io, distance_index_io]

        # Build secondary index to map from index Logical ID to Row ID.
        # Use save_file_path's hash value to retrieve the table.
        col_list = [
            ColumnDefinition(
                "logical_id",
                ColumnType.INTEGER,
                None,
                [],
                ColConstraintInfo(unique=True),
            ),
            ColumnDefinition(
                "row_id", ColumnType.INTEGER, None, [], ColConstraintInfo(unique=True)
            ),
        ]
        col_metadata = [
            CatalogManager().create_column_metadata(
                col.name, col.type, col.array_type, col.dimension, col.cci
            )
            for col in col_list
        ]
        tb_metadata = CatalogManager().create_metadata(
            "secondary_index_{}_{}".format(self.node.index_type, self.node.name),
            str(
                EVA_DEFAULT_DIR
                / INDEX_DIR
                / Path("{}_{}.secindex".format(self.node.index_type, self.node.name))
            ),
            col_metadata,
            identifier_column="logical_id",
            is_video=False,
        )
        StorageEngine.create(tb_metadata)

        # Write exact mapping for now.
        logical_id = [i for i in range(feat_size)]
        secondary_index = Batch(
            pd.DataFrame(
                data={"logical_id": logical_id, "row_id": deepcopy(logical_id)}
            )
        )
        StorageEngine.write(tb_metadata, secondary_index)

        # Persist index.
        faiss.write_index(index, str(save_file_path))

        # Save to catalog.
        CatalogManager().create_index(
            self.node.name,
            str(save_file_path),
            self.node.index_type,
            io_list,
        )

        yield Batch(
            pd.DataFrame(
                [f"Index {self.node.name} successfully added to the database."]
            )
        )

    def _create_index(self, index_type: IndexType, input_dim: int):
        if index_type == IndexType.HNSW:
            return faiss.IndexHNSWFlat(input_dim, 32)
        else:
            raise Exception(f"Index Type {index_type} is not supported.")
