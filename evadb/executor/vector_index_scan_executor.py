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
from typing import Iterator

import pandas as pd

from evadb.catalog.sql_config import IDENTIFIER_COLUMN
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import handle_vector_store_params
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.vector_index_scan_plan import VectorIndexScanPlan
from evadb.third_party.vector_stores.types import VectorIndexQuery
from evadb.third_party.vector_stores.utils import VectorStoreFactory
from evadb.utils.logging_manager import logger


# Helper function for getting row_id column alias.
def get_row_id_column_alias(column_list):
    for column in column_list:
        alias, col_name = column.split(".")
        if col_name == IDENTIFIER_COLUMN:
            return alias


class VectorIndexScanExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: VectorIndexScanPlan):
        super().__init__(db, node)

        self.index_name = node.index_name
        self.limit_count = node.limit_count
        self.search_query_expr = node.search_query_expr

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        # Fetch the index from disk.
        index_catalog_entry = self.catalog().get_index_catalog_entry_by_name(
            self.index_name
        )
        self.index_path = index_catalog_entry.save_file_path
        self.index = VectorStoreFactory.init_vector_store(
            self.node.vector_store_type,
            self.index_name,
            **handle_vector_store_params(self.node.vector_store_type, self.index_path),
        )

        # Get the query feature vector. Create a dummy
        # batch to retreat a single file path.
        dummy_batch = Batch(
            frames=pd.DataFrame(
                {"0": [0]},
            )
        )
        search_batch = self.search_query_expr.evaluate(dummy_batch)

        # Scan index. The search batch comes from the Open call.
        feature_col_name = self.search_query_expr.output_objs[0].name
        search_batch.drop_column_alias()
        search_feat = search_batch.column_as_numpy_array(feature_col_name)[0]
        search_feat = search_feat.reshape(1, -1)
        index_result = self.index.query(
            VectorIndexQuery(search_feat, self.limit_count.value)
        )
        # todo support queries over distance as well
        # distance_list = index_result.similarities
        row_id_np = index_result.ids

        # Load projected columns from disk and join with search results.
        row_id_col_name = None

        # handle the case where the index_results are less than self.limit_count.value
        num_required_results = self.limit_count.value
        if len(index_result.ids) < self.limit_count.value:
            num_required_results = len(index_result.ids)
            logger.warning(
                f"The index {self.index_name} returned only {num_required_results} results, which is fewer than the required {self.limit_count.value}."
            )

        res_row_list = [None for _ in range(num_required_results)]
        for batch in self.children[0].exec(**kwargs):
            column_list = batch.columns
            if not row_id_col_name:
                row_id_alias = get_row_id_column_alias(column_list)
                row_id_col_name = "{}.{}".format(row_id_alias, IDENTIFIER_COLUMN)

            # Nested join.
            for _, row in batch.frames.iterrows():
                for idx, rid in enumerate(row_id_np):
                    if rid == row[row_id_col_name]:
                        res_row = dict()
                        for col_name in column_list:
                            res_row[col_name] = row[col_name]
                        res_row_list[idx] = res_row

        yield Batch(pd.DataFrame(res_row_list))
