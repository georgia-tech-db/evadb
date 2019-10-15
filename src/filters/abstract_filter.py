"""
This file implements the inteface for filters

@Jaeho Bang
"""
import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod

class FilterTemplate(metaclass = ABCMeta):

  @abstractmethod
  def train(self, X:np.ndarray, y:np.ndarray):
    """
    Train all preprocessing models (if needed)
    :param X: data
    :param y: labels
    :return: None
    """
    pass


  @abstractmethod
  def predict(self, X:np.ndarray, premodel_name:str, postmodel_name:str)->np.ndarray:
    """
    This function is using during inference step.
    The scenario would be
    1. We have finished training
    2. The query optimizer knows which filters / models within will be best for a given query
    3. The query optimizer orders the inference for a specific filter / preprocessing model / postprocessing model

    :param X: data
    :param premodel_name: name of preprocessing model to use
    :param postmodel_name: name of postprocessing model to use
    :return: resulting labels
    """
    pass

  @abstractmethod
  def getAllStats(self)->pd.DataFrame:
    """
    This function returns all the statistics acquired after training the preprocessing models and postprocessing models

    :return:
    """
    pass
