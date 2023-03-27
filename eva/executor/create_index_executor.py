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
from pathlib import Path

import faiss
import numpy as np
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import IndexType
from eva.catalog.sql_config import IDENTIFIER_COLUMN
from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.plan_nodes.create_index_plan import CreateIndexPlan
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


def create_faiss_index(index_type: IndexType, input_dim: int):
    # Refernce to Faiss documentation.
    # IDMap: https://github.com/facebookresearch/faiss/wiki/Pre--and-post-processing#faiss-id-mapping
    # Other index types: https://github.com/facebookresearch/faiss/wiki/The-index-factory

    if index_type == IndexType.HNSW:
        # HSNW is the actual index. Faiss also provides
        # a secondary mapping (IDMap) to map from ID inside index to
        # our given ID.
        return faiss.IndexIDMap2(faiss.IndexHNSWFlat(input_dim, 32))


class CreateIndexExecutor(AbstractExecutor):
    def __init__(self, node: CreateIndexPlan):
        super().__init__(node)

    def exec(self, *args, **kwargs):
        catalog_manager = CatalogManager()
        if catalog_manager.get_index_catalog_entry_by_name(self.node.name):
            msg = f"Index {self.node.name} already exists."
            logger.error(msg)
            raise ExecutorError(msg)

        # Get the index type.
        index_type = self.node.index_type

        assert IndexType.is_faiss_index_type(
            index_type
        ), "Index type {} is not supported.".format(index_type)

        if IndexType.is_faiss_index_type(index_type):
            self._create_faiss_index()

        yield Batch(
            pd.DataFrame(
                [f"Index {self.node.name} successfully added to the database."]
            )
        )

    def _get_index_save_path(self) -> Path:
        index_dir = Path(ConfigurationManager().get_value("storage", "index_dir"))
        if not index_dir.exists():
            index_dir.mkdir(parents=True, exist_ok=True)
        return str(
            index_dir / Path("{}_{}.index".format(self.node.index_type, self.node.name))
        )

    def _create_faiss_index(self):
        try:
            catalog_manager = CatalogManager()

            # Get feature tables.
            feat_catalog_entry = self.node.table_ref.table.table_obj

            # Get feature column.
            feat_col_name = self.node.col_list[0].name
            feat_column = [
                col for col in feat_catalog_entry.columns if col.name == feat_col_name
            ][0]

            # Get udf function.
            udf_func = self.node.udf_func

            # Add features to index.
            # TODO: batch size is hardcoded for now.
            index = None
            input_dim = -1
            storage_engine = StorageEngine.factory(feat_catalog_entry)
            for input_batch in storage_engine.read(feat_catalog_entry, 1):
                if udf_func:
                    # Create index through UDF expression.
                    # UDF(input column) -> 2 dimension feature vector.
                    input_batch.modify_column_alias(feat_catalog_entry.name.lower())
                    feat_batch = self.node.udf_func.evaluate(input_batch)
                    feat_batch.drop_column_alias()
                    input_batch.drop_column_alias()
                    feat = feat_batch.column_as_numpy_array("features")[0]
                else:
                    # Create index on the feature table direclty.
                    # Pandas wraps numpy array as an object inside a numpy
                    # array. Use zero index to get the actual numpy array.
                    feat = input_batch.column_as_numpy_array(feat_col_name)[0]

                # Transform to 2-D.
                feat = feat.reshape(1, -1)

                if index is None:
                    input_dim = feat.shape[-1]
                    index = create_faiss_index(self.node.index_type, input_dim)

                # Row ID for mapping back to the row.
                row_id = input_batch.column_as_numpy_array(IDENTIFIER_COLUMN)[0]
                index.add_with_ids(feat, np.array([row_id]))

            # Persist index.
            faiss.write_index(index, self._get_index_save_path())

            # Save to catalog.
            catalog_manager.insert_index_catalog_entry(
                self.node.name,
                self._get_index_save_path(),
                self.node.index_type,
                feat_column,
                udf_func.signature() if udf_func else None,
            )
        except Exception as e:
            # Roll back in reverse order.
            # Delete on-disk index.
            index_path = Path(self._get_index_save_path())
            if index_path.exists():
                index_path.unlink()

            # Throw exception back to user.
            raise ExecutorError(str(e))
