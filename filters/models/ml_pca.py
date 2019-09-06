

import numpy as np
import time
from filters.models.ml_base import MLBase
from sklearn.decomposition import PCA


class MLPCA(MLBase):
  def __init__(self, **kwargs):
    super(MLPCA, self).__init__(MLBase)
    if kwargs:
      self.model = PCA(random_state=0)
    else:
      self.model = PCA(**kwargs)


  def train(self, X :np.ndarray, y :np.ndarray):
    n_samples = X.shape[0]
    division = int(n_samples * self.division_rate)
    X_val = X[division:]
    y_val = y[division:]

    tic = time.time()
    self.model.score(X_val, y_val)
    toc = time.time()
    val_samples = X_val.shape[0]

    self.C = (toc - tic) / val_samples

  def predict(self, X :np.ndarray):
    return self.model.fit_transform(X)

