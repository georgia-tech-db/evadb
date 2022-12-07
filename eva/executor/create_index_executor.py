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
import numpy as np
import os
import pandas as pd
from sqlalchemy import true

from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.create_index_plan import CreateIndexPlan
from eva.utils.logging_manager import logger
from eva.configuration.configuration_manager import ConfigurationManager
from eva.catalog.catalog_manager import CatalogManager

from eva.catalog.column_type import FaissIndexType


class CreateIndexExecutor(AbstractExecutor):
    def __init__(self, node: CreateIndexPlan):
        super().__init__(node)
        self.table_name = node.table_ref.table.table_name
        self.udf_name = node.col_list[0].name
        self.index_name = node.index_name
        self.catalog_manager = CatalogManager()
        self.faiss_idx_type = node.faiss_idx_type

    def validate(self):
        pass

    def exec(self):
        # check if index exists. if it exists, nothing to do
        if self.catalog_manager.get_index(self.table_name, self.udf_name,
                                          self.faiss_idx_type) is not None:
            msg = f"Index of UDF {self.udf_name} already exists on the table named {self.table_name}."
            return Batch(pd.DataFrame([msg]))

        scan_executor = self.children[0]
        output = scan_executor.exec()

        all_output_vec = None
        if output:
            batch_list = list(output)
            all_output_vec = Batch.concat(batch_list, copy=False)
        else:
            raise RuntimeError("When creating index, child select (project) executor"
                               " didn't return any data.")

        # We want to know the number of outputs of this UDF.
        udf_meta = self.catalog_manager.get_udf_by_name(self.udf_name)
        udf_outputs = self.catalog_manager.get_udf_outputs(udf_meta)

        need_cache: bool = self.catalog_manager.get_res_cache(self.table_name, self.udf_name) \
                           is None
        
        index = None
        # We use FAISS to create an index only when the model outputs *one* feature vector
        if len(udf_outputs) == 1:
            # Use FAISS to create index on `all_output_vec` here
            feature_vecs = np.concatenate(all_output_vec.frames["featureextractor.features"])
            n, d = feature_vecs.shape
            
            # TODO: Implement different indexing methods
            idx_type = self.faiss_idx_type
            if idx_type == FaissIndexType.FlatL2:
                index = faiss.IndexFlatL2(d)
            elif idx_type == FaissIndexType.FlatIP:
                index = faiss.IndexFlatIP(d)
            elif idx_type == FaissIndexType.IVFFlat:

                nlist = 8  # number of cells/clusters to partition data into
                if len(feature_vecs) < 200:
                    nlist = 4
                elif len (feature_vecs) < 1600:
                    nlist = 8
                elif len (feature_vecs) < 6400:
                    nlist = 16
                elif len (feature_vecs) < 25600:
                    nlist = 32
                else:
                    nlist = 128

                quantizer = faiss.IndexFlatIP(d)  # how the vectors will be stored/compared
                index = faiss.IndexIVFFlat(quantizer, d, nlist)
                index.train(feature_vecs)  # we must train the index to cluster into cells
            else:
                raise NotImplementedError("Unsupported faiss index type.")

            index.add(feature_vecs)
            msg = self.store_index(index, all_output_vec,
                                   is_faiss_index=True, is_cache=need_cache, faiss_idx_type=idx_type)
        # otherwise, we cache the result of this UDF
        else:
            msg = self.store_index(index, all_output_vec,
                                   is_faiss_index=False, is_cache=need_cache, faiss_idx_type=None)
    
        return Batch(pd.DataFrame([msg]))
    
    def store_index(self,
                    index: faiss.Index,
                    output_vec: Batch,
                    is_faiss_index: bool,
                    is_cache: bool,
                    faiss_idx_type: FaissIndexType) -> str:

        if not (is_cache or is_faiss_index):
            return "create index: nothing to do."

        eva_idx_dir = ConfigurationManager().get_index_dir()

        if not os.path.exists(eva_idx_dir):
            os.mkdir(eva_idx_dir)
        
        idx_file_name = None
        if is_faiss_index:
            # Store index to FAISS file
            idx_file_name = f'{self.table_name}_{self.udf_name}_{str(faiss_idx_type)}_index.index'

            idx_file_path = os.path.join(eva_idx_dir, idx_file_name)
            faiss.write_index(index, idx_file_path)
            
        # Store UDF output to pickle file
        output_vec_file_name = None
        if is_cache:
            output_vec_file_name = f"{self.table_name}_{self.udf_name}_output.out"
            output_vec_file_path = os.path.join(eva_idx_dir, output_vec_file_name)
            output_vec.frames.to_pickle(output_vec_file_path)

        # Add a record to the catalog
        self.catalog_manager.create_index(
            idx_name=self.index_name,
            faiss_idx_type=faiss_idx_type if is_faiss_index else None,
            is_faiss_idx=is_faiss_index,
            is_res_cache=is_cache,
            res_cache_path=output_vec_file_name,
            faiss_idx_path=idx_file_name,
            udf_name=self.udf_name,
            table_name=self.table_name
        )

        if is_faiss_index:
            return f"Index of UDF {self.udf_name} successfully added to the " \
                   f"table named {self.table_name}."
        elif is_cache:
            return f"UDF {self.udf_name} has multiple outputs, only its output " \
                   f"is cached for table {self.table_name}."
        else:
            pass
