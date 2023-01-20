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
from typing import Iterator

import faiss
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.sql_config import IDENTIFIER_COLUMN
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.plan_nodes.faiss_index_scan_plan import FaissIndexScanPlan


# Helper function for getting row_id column alias.
def get_row_id_column_alias(column_list):
    for column in column_list:
        alias, col_name = column.split(".")
        if col_name == IDENTIFIER_COLUMN:
            return alias


class FaissIndexScanExecutor(AbstractExecutor):
    def __init__(self, node: FaissIndexScanPlan):
        super().__init__(node)
        self.index_name = node.index_name
        self.limit_count = node.limit_count
        self.search_query_expr = node.search_query_expr

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        catalog_manager = CatalogManager()

        # Fetch the index from disk.
        index_catalog_entry = catalog_manager.get_index_catalog_entry_by_name(
            self.index_name
        )
        index = faiss.read_index(index_catalog_entry.save_file_path)

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
        dis_np, row_id_np = index.search(search_feat, self.limit_count.value)

        distance_list, row_id_list = [], []
        for dis, row_id in zip(dis_np[0], row_id_np[0]):
            distance_list.append(dis)
            row_id_list.append(row_id)

        # Load projected columns from disk and join with search results.
        row_id_col_name = None
        res_row_list = [None for _ in range(self.limit_count.value)]
        for batch in self.children[0].exec():
            column_list = batch.columns
            if not row_id_col_name:
                row_id_alias = get_row_id_column_alias(column_list)
                row_id_col_name = "{}.{}".format(row_id_alias, IDENTIFIER_COLUMN)

            # Nested join.
            for _, row in batch.frames.iterrows():
                for idx, rid in enumerate(row_id_list):
                    if rid == row[row_id_col_name]:
                        res_row = dict()
                        for col_name in column_list:
                            res_row[col_name] = row[col_name]
                        res_row_list[idx] = res_row

        yield Batch(pd.DataFrame(res_row_list))
