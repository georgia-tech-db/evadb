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
from sklearn.neighbors.kde import KernelDensity


class KernelDensityWrapper:
    # A wrapper class for sklearn kde to match the other models and wrap the
    # logic behind using kde for classification

    # need .fit function
    # need .predict function

    def __init__(self, kernel='guassian', bandwidth=0.2):
        self.kernels = []  # assume everything is one shot
        self.kernel = kernel
        self.bandwidth = bandwidth

    def fit(self, X, y):
        unique_vals = np.unique(y)
        unique_vals = np.sort(unique_vals)
        if len(unique_vals) == 1:
            kde = KernelDensity(kernel=self.kernel, bandwidth=self.bandwidth)
            kde.fit(X[y == unique_vals[0]])
            if unique_vals[0] == 0:
                self.kernels.append(kde)
                self.kernels.append(None)
            else:
                self.kernels.append(None)
                self.kernels.append(kde)

        else:
            assert(len(unique_vals) == 2)
            kde = KernelDensity(kernel=self.kernel, bandwidth=self.bandwidth)
            kde.fit(X[y == 0])
            self.kernels.append(kde)

            kde = KernelDensity(kernel=self.kernel, bandwidth=self.bandwidth)
            kde.fit(X[y == 1])
            self.kernels.append(kde)

    def predict(self, X):
        # assume everything is one-shot
        scores = []
        n_samples, _ = X.shape
        for kernel in self.kernels:
            if kernel is None:
                scores.append(np.array([0] * n_samples))
            else:
                log_dens = kernel.score_samples(X)
                probs = np.exp(log_dens)
                scores.append(probs)
        scores = np.array(scores)

        return np.argmax(scores, axis=1)

    def score(self, X, y):
        assert len(self.kernels) != 0
        y_preds = self.predict(X)
        return float(np.sum(y == y_preds)) / len(y_preds)
