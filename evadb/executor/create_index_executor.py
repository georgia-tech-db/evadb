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

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import ExecutorError, handle_vector_store_params
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.create_index_plan import CreateIndexPlan
from evadb.third_party.vector_stores.types import FeaturePayload
from evadb.third_party.vector_stores.utils import VectorStoreFactory
from evadb.utils.logging_manager import logger


class CreateIndexExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: CreateIndexPlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        if self.catalog().get_index_catalog_entry_by_name(self.node.name):
            msg = f"Index {self.node.name} already exists."
            logger.error(msg)
            raise ExecutorError(msg)

        self.index_path = self._get_index_save_path()
        self.index = None
        self._create_index()

        yield Batch(
            pd.DataFrame(
                [f"Index {self.node.name} successfully added to the database."]
            )
        )

    def _get_index_save_path(self) -> Path:
        index_dir = Path(self.config.get_value("storage", "index_dir"))
        if not index_dir.exists():
            index_dir.mkdir(parents=True, exist_ok=True)
        return str(
            index_dir
            / Path("{}_{}.index".format(self.node.vector_store_type, self.node.name))
        )

    def _create_index(self):
        try:
            # Get feature column.
            feat_column = self.node.col_list[0].col_object

            # Add features to index.
            input_dim = -1
            for input_batch in self.children[0].exec():
                row_ids = input_batch.column_as_numpy_array(input_batch.columns[0])
                features = input_batch.column_as_numpy_array(input_batch.columns[1])

                for row_id, feat in zip(row_ids, features):
                    row_feat = feat.reshape(1, -1)
                    if self.index is None:
                        input_dim = row_feat.shape[1]
                        self.index = VectorStoreFactory.init_vector_store(
                            self.node.vector_store_type,
                            self.node.name,
                            **handle_vector_store_params(
                                self.node.vector_store_type, self.index_path
                            ),
                        )
                        self.index.create(input_dim)

                    # Row ID for mapping back to the row.
                    self.index.add([FeaturePayload(row_id, row_feat)])

            # Persist index.
            self.index.persist()

            # Save to catalog.
            self.catalog().insert_index_catalog_entry(
                self.node.name,
                self.index_path,
                self.node.vector_store_type,
                feat_column,
                self.node.udf_func.signature() if self.node.udf_func else None,
            )
        except Exception as e:
            # Delete index.
            if self.index:
                self.index.delete()

            # Throw exception back to user.
            raise ExecutorError(str(e))
