

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


  def train(self, X :np.ndarray, y :np.ndarray):
    n_samples = X.shape[0]

    self.model.fit_transform(X)


    tic = time.time()
    self.model.transform(X)
    toc = time.time()

    self.C = (toc - tic) / n_samples


  def predict(self, X :np.ndarray):
    return self.model.transform(X)

