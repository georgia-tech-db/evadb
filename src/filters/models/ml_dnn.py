"""
Shallow Neural Network Wrapper

@Jaeho Bang
"""

import numpy as np
import time
from sklearn.neural_network import MLPClassifier
from filters.models.ml_base import MLBase


class MLMLP(MLBase):
    def __init__(self, **kwargs):
        super(MLMLP, self).__init__()
        if kwargs:
            self.model = MLPClassifier(solver='lbfgs', alpha=1e-5,
                                   hidden_layer_sizes=(5, 2), random_state=1)
        else:
            self.model = MLPClassifier(**kwargs)


    def train(self, X :np.ndarray, y :np.ndarray):
        n_samples = X.shape[0]
        X = X / 255.0
        X = X.reshape(n_samples, -1)

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

    def predict(self, X :np.ndarray):
        n_samples = X.shape[0]
        X = X / 255.0
        X = X.reshape(n_samples, -1)
        return self.model.predict(X)

