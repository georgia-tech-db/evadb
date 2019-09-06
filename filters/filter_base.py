"""
This file implements the inteface for filters

@Jaeho Bang
"""
import numpy as np
from abc import ABCMeta, abstractmethod

class FilterBase(ABCMeta):

  def __init__(self):
    self.pre_models = {}
    self.post_models = {}

  def addPreModel(self, model_name, model):
    """
    Add preprocessing machine learning/statistical models such as PCA, Sampling, etc
    :param model_name: name of model must be string
    :param model: model
    :return: None
    """
    self.pre_models[model_name] = model

  def addPostModel(self, model_name, model):
    """
    Add postprocessing machine learning/statistical models such as SVM, DNN, random forest, etc
    :param model_name: name of model must be string
    :param model: model
    :return: None
    """
    self.post_models[model_name] = model

  def deletePreModel(self, model_name):
    """
    Delete preprocessing model from models dictionary
    :param model_name: name of model
    :return: None
    """
    if model_name in self.pre_models.keys():
      self.pre_models.pop(model_name)
    else:
      print("model name not found in pre model dictionary..")
      print("  ", self.pre_models.keys(), "are available")


  def deletePostModel(self, model_name):
    """
    Delete postprocessing model from models dictionary
    :param model_name: name of model
    :return: None
    """
    if model_name in self.post_models.keys():
      self.post_models.pop(model_name)
    else:
      print("model name not found in post model dictionary..")
      print("  ", self.post_models.keys(), "are available")


  @abstractmethod
  def trainPreModels(self, X:np.ndarray, y:np.ndarray):
    """
    Train all preprocessing models (if needed)
    :param X: data
    :param y: labels
    :return: None
    """
    pass


  @abstractmethod
  def trainPostModels(self, X:np.ndarray, y:np.ndarray):
    """
    Train all postprocessing models (if needed)
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
  def getAllStats(self):
    """
    This function returns all the statistics acquired after training the preprocessing models and postprocessing models

    :return:
    """
    pass
