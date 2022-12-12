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
import torch
import faiss
import numpy as np
import pandas as pd

from eva.executor.executor_utils import ExecutorError
from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.udfs.feature_extractor import FeatureExtractor
from eva.catalog.models.df_column import DataFrameColumn
from eva.storage.storage_engine import StorageEngine


class Similarity(AbstractUDF):
    def _get_distance(self, numpy_distance):
        return numpy_distance[0][0]

    def setup(self):
        pass

    @property
    def name(self):
        return "Similarity"

    def forward(
        self, 
        open_df: pd.DataFrame, 
        input_column: DataFrameColumn, 
        feat_extractor: FeatureExtractor
    ) -> pd.DataFrame:
        """
        Get similarity score between two feature vectors: 1. feature vector of an opened image;
        and 2. feature vector from base table.
        """

        # TODO: check if an index exists.

        # Check pairwise distance.
        open_feat = feat_extractor(open_df)
        open_feat_np = open_feat["features"].to_numpy()[0]

        input_df_metadata = input_column.dataset
        storage_engine = StorageEngine.factory(input_df_metadata)

        for row in storage_engine.read(input_df_metadata, 1):
            feat_np = row.column_as_numpy_array(input_column.name)[0]
            # Use L2 as default, but since it is exact matching, it does not
            # matter which distance metric that we use.
            distance_np = faiss.pairwise_distances(open_feat_np, feat_np)
            distance = self._get_distance(distance_np)
            yield()