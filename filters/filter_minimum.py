"""
This file is composed of the composing preliminary and post filtering techniques.



@Jaeho Bang
"""

import numpy as np
import pandas as pd

from filters.filter_base import FilterBase
from filters.models.ml_randomforest import MLRandomForest


# Meant to be a black box for trying all models available and returning statistics and model for
# the query optimizer to choose for a given query

"""
Each Filter object considers 1 specific query. Either the query optimizer or the pipeline needs to manage a diction of Filters
 
"""

class FilterMinimum(FilterBase):
  def __init__(self):
    super(FilterMinimum, self).__init__()

    rf = MLRandomForest()
    self.addPostModel('rf', rf)

  def trainPreModels(self):
    # There are no pre models in this file
    pass

  def trainPostModels(self, X, y):
    for model_name, model in self.post_models.items():
      model.train(X, y)


  def predict(self, X:np.ndarray, pre_model_name:str = None, post_model_name:str = None)->np.ndarray:
    pre_model_names = self.pre_models.keys()
    post_model_names = self.post_models.keys()
    pre_model = None
    post_model = None
    if pre_model_name in pre_model_names:
      pre_model = self.pre_models[pre_model_name]
    if post_model_name in post_model_names:
      post_model = self.post_models[post_model_name]

    ## If we haven't found the post model, there is no prediction to be done
    ## so we must raise an error
    if post_model is None:
      print("No Post Model is found.")
      print("  Given:", post_model_name)
      print("  Available:", post_model_names)
      return np.array([])

    if pre_model is not None:
      X = pre_model.predict(X)
    return post_model.predict(X)


  def getAllStats(self):
    """
    TODO!!!!
    will need to organize the stats in a panda format where rows correspond to models and cols correspond to RCA values
    One thing to think about is to whether to separate the stats between preprocessing models or post processing models....
    
    :return:
    """
    pass


