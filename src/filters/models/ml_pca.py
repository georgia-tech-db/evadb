# coding=utf-8
# Copyright 2018-2020 EVA
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


import numpy as np
import time
from filters.models.ml_base import MLBase
from sklearn.decomposition import PCA


class MLPCA(MLBase):
    def __init__(self, **kwargs):
        super(MLPCA, self).__init__()
        if kwargs:
            self.model = PCA(random_state=0)
        else:
            self.model = PCA(**kwargs)

    def train(self, X: np.ndarray, y: np.ndarray):
        n_samples = X.shape[0]

        self.model.fit_transform(X)

        tic = time.time()
        self.model.transform(X)
        toc = time.time()

        self.C = (toc - tic) / n_samples

    def predict(self, X: np.ndarray):
        return self.model.transform(X)
