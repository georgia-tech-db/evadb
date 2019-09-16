"""
Linear SVM wrapper

@Jaeho Bang
"""

import time

import numpy as np
from sklearn.svm import LinearSVC

from filters.models.ml_base import MLBase


class MLSVM(MLBase):
    def __init__(self, **kwargs):
        super(MLSVM, self).__init__(MLBase)
        if kwargs:
            self.model = LinearSVC(random_state=0)
        else:
            self.model = LinearSVC(**kwargs)

    def train(self, X: np.ndarray, y: np.ndarray):
        n_samples = X.shape[0]
        division = int(n_samples * self.division_rate)
        X_train = X[:division]
        y_train = y[:division]
        X_val = X[division:]
        y_val = y[division:]

        self.model.fit(X_train, y_train)
        tic = time.time()
        score = self.model.score(X_val, y_val)
        toc = time.time()
        val_samples = X_val.shape[0]
        y_hat = self.model.predict(X_val)

        self.C = (toc - tic) / val_samples
        self.A = score
        self.R = 1 - float(sum(y_hat)) / len(y_hat)

    def predict(self, X: np.ndarray):
        return self.model.predict(X)
