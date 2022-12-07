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
import pandas as pd
import cv2
import numpy as np
import faiss
import os
from eva.catalog.column_type import ColumnType
from eva.parser.table_ref import TableInfo, TableRef
from eva.models.storage.batch import Batch

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.parser.create_index_statement import CreateIndexStatement

from eva.expression.abstract_expression import (
    AbstractExpression,
    ExpressionReturnType,
    ExpressionType,
)

from eva.expression.function_expression import FunctionExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.catalog.column_type import FaissIndexType, DistanceMetric

"""
A binary expression.
Semantically, the left-hand side parameter is the result of the UDF execution (feature vector),
and the right-hand side parameter is the path of the images used for comparison.
"""
class LikeExpression(AbstractExpression):
    # Map distance metric to index type
    # Since the LIKE expression contains a parameter `metric`,
    # We want to know the type of index corresponding to a given distance metric.
    dist_metric_to_index_type: dict = {
        DistanceMetric.L2: [FaissIndexType.FlatL2, FaissIndexType.IVFFlat],
        DistanceMetric.L1: [],
        DistanceMetric.InnerProduct: [FaissIndexType.FlatIP]
    }

    def __init__(
        self,
        left: FunctionExpression,
        right: ConstantValueExpression,
        flip: bool,
        distance_metric: DistanceMetric,
        table_info: TableInfo = None
    ):
        self.table_info = table_info
        self.similar_idx = None
        self.udf_func = left
        self.metric = distance_metric
        self.src_img_path = right.value if right.v_type == ColumnType.TEXT else None

        children = [left, right]
        super().__init__(ExpressionType.LIKE, ExpressionReturnType.BOOLEAN, children)


    def evaluate(self, batch: Batch, **kwargs) -> Batch:

        if self.similar_idx is None:
            self.compute_similar_idx()

        data_frame = batch.frames
        
        id_col_name = self.table_info.table_name.lower() + ".id"
        data_frame = pd.DataFrame(data_frame[id_col_name].isin(self.similar_idx))
        # EVA requires this column to be 0
        data_frame.columns.values[0] = 0
        if "mask" in kwargs:
            data_frame = data_frame.iloc[kwargs["mask"]]
        return Batch(data_frame)
        
    # Compute a set containing the index of similar frames
    def compute_similar_idx(self):
        if self.src_img_path is None:
            raise ValueError("Like Expression: invalid source image path.")

        if self.table_info is None:
            raise ValueError("Like Expression: didn't receive table info.")

        feature_vector = self.compute_feature_vector(self.src_img_path)
        index = self.get_faiss_index()

        # how to determine this value ?
        topK = 12
        _, similar_idx = index.search(feature_vector, topK)
        
        self.similar_idx = similar_idx[0]

    def get_faiss_index(self) -> faiss.Index:

        if self.metric not in LikeExpression.dist_metric_to_index_type:
            raise NotImplementedError("Unsupported distance metric.")

        index_types = LikeExpression.dist_metric_to_index_type[self.metric]
        if len(index_types) == 0:
            raise NotImplementedError("Unsupported distance metric.")

        # Retrieve all available indexes
        all_index = CatalogManager().get_all_index(self.table_info.table_name,
                                                    self.udf_func.name)

        index_meta = None
        # If no index available, create one.
        if all_index is None or len(all_index) == 0:
            if self.create_index(index_types[0]):
                return self.get_faiss_index()
            else:
                raise ValueError("LIKE: No available index. Attempt to create index failed.")
        else:
            # Now we just pick the first one from all the indexes that
            # match the distance metric requirements.
            for idx_info in all_index:
                if idx_info.faiss_idx_type in index_types:
                    index_meta = idx_info
                    break

        if index_meta is None:
            raise ValueError("LIKE: No viable index for the given distance metric.")

        index_file_path = os.path.join(ConfigurationManager().get_index_dir(),
                                        index_meta.faiss_idx_path)
        return faiss.read_index(index_file_path)

    # compute the feature vector of the specified image
    def compute_feature_vector(self, img_path: str) -> object:
        img_bgr = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        # udf requires the images to be in a batch
        # so expand the dimension by 1
        img_rgb = img_rgb[None, :]
        
        # `_gpu_enabled_function` seems to be a private function
        # Although we could call `udf_func.evaluate directly,
        # there is too much data conversion involved
        func = self.udf_func._gpu_enabled_function()
        feature_vec = func(img_rgb)["features"].to_numpy()[0]
        return feature_vec

    def create_index(self, index_type: FaissIndexType):
        index_name = "unnamed_" + str(index_type)
        create_index_stmt = CreateIndexStatement(index_name,
                                                 True,
                                                 TableRef(self.table_info),
                                                 [self.udf_func],
                                                 index_type)
        try:
            from eva.server.command_handler import execute_query_fetch_all
            execute_query_fetch_all(create_index_stmt)
            return True
        except Exception as e:
            return False


    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LikeExpression):
            return False
        return is_subtree_equal and self.etype == other.etype

    def __hash__(self) -> int:
        return super().__hash__()
