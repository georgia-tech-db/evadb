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
from src.filters.research_filter import FilterResearch
from src.filters.models.ml_pca import MLPCA
from src.filters.models.ml_dnn import MLMLP
import numpy as np
import unittest


class ResearchFilter_Test(unittest.TestCase):

    def test_FilterResearch(self):
        # Construct the filter research and test it with randomized values
        # Idea is just to run it and make sure that things run to completion
        # No actual output or known inputs are tested
        filter = FilterResearch()

        # Set up the randomized input for testing
        X = np.random.random([100, 30])
        y = np.random.random([100])
        y *= 10
        y = y.astype(np.int32)

        # Split into training and testing data
        division = int(X.shape[0] * 0.8)
        X_train = X[:division]
        X_test = X[division:]
        y_iscar_train = y[:division]
        y_iscar_test = y[division:]

        filter.addPostModel("dnn", MLMLP())
        filter.addPreModel("pca", MLPCA())

        filter.train(X_train, y_iscar_train)
        y_iscar_hat = filter.predict(X_test, pre_model_name='pca',
                                     post_model_name='dnn')
        filter.getAllStats()

        filter.deletePostModel("dnn")
        filter.deletePreModel("pca")
