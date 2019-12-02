from src.filters.minimum_filter import FilterMinimum
import numpy as np

def test_FilterMinimum():
    # Construct the filter minimum and test it with randomized values
    # The idea is just to run it and make sure that things run to completion
    # No actual output or known inputs are tested
    filter = FilterMinimum()

    # Set up the randomized input for testing
    X = np.random.random([100,30,30,3])
    y = np.random.random([100])
    y *= 10
    y = y.astype(np.int32)

    # Split into training and testing data
    division = int(X.shape[0] * 0.8)
    X_train = X[:division]
    X_test = X[division:]
    y_iscar_train = y[:division]
    y_iscar_test = y[division:]

    filter.train(X_train, y_iscar_train)
    y_iscar_hat = filter.predict(X_test, post_model_name='rf')
    stats = filter.getAllStats()