import time
import os, sys
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
#import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import xml.etree.ElementTree as ET
from scipy import ndimage
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img



# Meant to be a black box for trying all models available and returning statistics and model for
# the query optimizer to choose for a given query

class PP_gen:


  def __init__(self):
    self.model_library = {} #KDE, SVM, NN - this should be a mapping of model name to model CONSTRUCTOR
    self.model_library_pre = {None} #feature hashing, PCA, None - Separated to do mix and match
    self.category_libary = {} #save the trained model
    self.category_stats = {} #save the statistics related to the model, although most stats are embedded in the model,
                             #made this just in case there could be stats that are not saved
    #TODO: append the models to model_library (feature hashing, PCA, KDE, SVM, NN)


  # Give category_name and its parsed X, Y, also provide arguments if you want to specify model arguments
  def train(self, category_name, X, Y, args = None):
    for model_name in self.model_libary:
      model = self.model_library[model_name]
      #TODO: try fitting and save statistics - we will have this information available for QO (Query Optimizer)
      model.fit(X,Y)

      self.category_stats[category_name] = {model_name: {"reduction_rate": model.score(),
                                                           "false_negative_rate":model.......,
                                                         "time_to_train": }

      self.category_library[category_name] = {model_name: model}


  def getCategoryInfo(self, category_name):
    return self.category_stats[category_name]

  def getCategoryModels(self, category_name):
    return self.category_library[category_name]


  # returns list of model names
  def getModelLibrary(self):
    return self.model_library.keys()




