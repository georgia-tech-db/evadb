from src.filters.kdewrapper import KernelDensityWrapper
import numpy as np

def test_KD_Wrapper():
    # Construct the filter research and test it with randomized values
    # The idea is just to run it and make sure that things run to completion
    # No actual output or known inputs are tested
    wrapper = KernelDensityWrapper()

    # Set up the randomized input for testing
    X = np.random.random([100, 30])
    y = np.random.randint(2, size = 100)
    y = y.astype(np.int32)

    # Split into training and testing data
    division = int(X.shape[0] * 0.8)
    X_train = X[:division]
    X_test = X[division:]
    y_iscar_train = y[:division]
    y_iscar_test = y[division:]

    wrapper.fit(X_train, y_iscar_train)
    y_iscar_hat = wrapper.predict(X_test)
    #scores = wrapper.getAllStats()