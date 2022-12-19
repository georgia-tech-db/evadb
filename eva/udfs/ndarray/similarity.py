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

from eva.udfs.abstract.abstract_udf import AbstractUDF


class Similarity(AbstractUDF):
    def _get_distance(self, numpy_distance):
        return numpy_distance[0][0]

    def setup(self):
        pass

    @property
    def name(self):
        return "Similarity"

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get similarity score between two feature vectors: 1. feature vector of an opened image;
        and 2. feature vector from base table.
        """

        def _similarity(row: pd.Series) -> float:
            open_feat_np, base_feat_np = (
                row.iloc[0],
                row.iloc[1],
            )

            # TODO: currently system takes care of feature vector shape
            # transformation. Improve this later on.
            # Transform to 2D.
            open_feat_np = open_feat_np.reshape(1, -1)
            base_feat_np = base_feat_np.reshape(1, -1)
            distance_np = faiss.pairwise_distances(open_feat_np, base_feat_np)

            return self._get_distance(distance_np)

        ret = pd.DataFrame()
        ret["distance"] = df.apply(_similarity, axis=1)
        return ret
