import numpy as np
from sklearn.neighbors.kde import KernelDensity




class KernelDensityWrapper:
  #A wrapper class for sklearn kde to match the other models and wrap the logic behind using kde for classification



  #need .fit function
  #need .predict function

  def __init__(self, kernel='guassian', bandwidth=0.2):
    self.kernels = [] #assume everything is one shot
    self.kernel = kernel
    self.bandwidth = bandwidth

  def fit(self, X, y):
    unique_vals = np.unique(y)
    unique_vals = np.sort(unique_vals)
    assert(unique_vals[0] == 0)
    assert(unique_vals[1] == 1)


    kde = KernelDensity(kernel=self.kernel, bandwidth=self.bandwidth)
    kde.fit(X[y == 0])
    self.kernels.append(kde)

    kde = KernelDensity(kernel=self.kernel, bandwidth=self.bandwidth)
    kde.fit(X[y == 1])
    self.kernels.append(kde)


  def predict(self, X):
    ##assume everything is one-shot
    score = self.kernels[0].score_samples(X)
    scores = np.array(score)
    score = self.kernels[1].score_samples(X)
    scores = np.vstack((scores, score))

    return np.argmax(scores, axis = 0)

  def score(self, X, y):
    assert len(self.kernels) != 0
    y_preds = self.predict(X)
    return float(np.sum(y == y_preds)) / len(y_preds)


