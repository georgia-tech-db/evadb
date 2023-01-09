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
import faiss
import pandas as pd

from typing import Iterator

from eva.catalog.catalog_manager import CatalogManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.plan_nodes.faiss_index_scan_plan import FaissIndexScanPlan
from eva.utils.logging_manager import logger


class FaissIndexScanExecutor(AbstractExecutor):
    def __init__(self, node: FaissIndexScanPlan):
        super().__init__(node)
        self.index_name = node.index_name
        self.query_num = node.query_num
        self.query_expr = node.query_expr

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        catalog_manager = CatalogManager()

        # Fetch the index from disk.
        index_catalog_entry = catalog_manager.get_index_catalog_entry_by_name(self.index_name)
        index = faiss.read_index(index_catalog_entry.save_file_path)

        # Get the query feature vector.
        dummy_batch = Batch(frames=pd.DataFrame(
            {"0": [0]},
        ))
        search_batch = self.query_expr.evaluate(dummy_batch)

        # Scan index.
        search_batch.drop_column_alias()
        search_feat = search_batch.column_as_numpy_array("features")[0]
        search_feat = search_feat.reshape(1, -1)
        dis_np, row_id_np = index.search(search_feat, self.query_num.value)

        # Wrap results.
        distance_list, row_id_list = [], []
        for dis, row_id in zip(dis_np[0], row_id_np[0]):
            distance_list.append(dis)
            row_id_list.append(row_id)

        yield Batch(pd.DataFrame({
            "distance": distance_list,
            "row_id": row_id_list,
        }))
