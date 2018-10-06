
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

import filters.load as load
import filters.pp as pp
import query_optimizer.query_optimizer as qo


#TODO: Fill this file in with the components loaded from other files
class Pipeline:
  """1. Load the dataset
     2. Load the QO
     3. Load the Filters
     4. Load the Central Network (RFCNN, SVM for other labels etc)
     5. Listen to Queries
     6. Give back result"""

  def __init__(self):
    self.load = load.Load()
    self.pp = pp.PP()
    self.qo = qo.QueryOptimizer()

  # We have access to train and test dataset -> Used for finding the score and evaluation
  def filter_performance_test(self):
    start_time = time.time()

    data, label_dict = self.load.load_dataset()
    nsamples, nx, ny, nc = data.shape
    data = data.reshape((nsamples, nx * ny * nc))

    #TODO: Split the dataset into train, val, test (val should be used for evaluating the pps
    #TODO: (continued) -> Need to look at paper to make sure it is the correct way
    X = pd.DataFrame(data)
    for label in label_dict:
      y = pd.Series(label_dict[label])
      X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=42)
      break

    train_index = X_train.index.values
    test_index = X_test.index.values
    label_dict_train = {}
    label_dict_test = {}
    for label in label_dict:
      label_dict_train[label] = label_dict[label][train_index]
      label_dict_test[label] = label_dict[label][test_index]


    print("--- Total Execution Time for loading the dataset: %.3f seconds ---" % (time.time() - start_time))

    start_time = time.time()
    self.pp.train_all(X_train, label_dict_train)
    print("--- Total Execution Time for training the dataset : %.3f seconds ---" % (time.time() - start_time))
    if __debug__:
      print X_train.shape
      print X_test.shape

    category_stats = self.pp.evaluate(X_test, label_dict_test)
    print category_stats
    return

  # Actual run of the pipeline
  def run(self):
    start_time = time.time()

    data, label_dict = self.load.load_dataset()
    print("--- Total Execution Time for loading the dataset: %.3f seconds ---" % (time.time() - start_time))

    start_time = time.time()
    self.pp.train_all(data, label_dict)
    print("--- Total Execution Time for training the dataset : %.3f seconds ---" % (time.time() - start_time))

    return

if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.test()

