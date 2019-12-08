from src.filters.minimum_filter import FilterMinimum
from src.filters.models.ml_pca import MLPCA
from src.filters.models.ml_dnn import MLMLP
import numpy as np
import unittest


class FilterMinimum_Test(unittest.TestCase):

    def test_FilterMinimum(self):
        # Construct the filter minimum and test it with randomized values
        # Idea is just to run it and make sure that things run to completion
        # No actual output or known inputs are tested
        filter = FilterMinimum()

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
        stats = filter.getAllStats()

        filter.deletePostModel("dnn")
        filter.deletePreModel("pca")