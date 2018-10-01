import time
import os, sys
import numpy as np
#import matplotlib.pyplot as plt


from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import xml.etree.ElementTree as ET
from scipy import ndimage
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from sklearn.feature_extraction import FeatureHasher
from sklearn.decomposition import PCA


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


  #TODO: need to perform feature hashing after all the categories are inputted??
  def feature_hashing(self):
    category_count = len(self.category_libary.keys())
    if category_count < 2:
      return

    h = FeatureHasher(n_features=category_count)
    D = []
    for i in range(category_count):
      D.append()
    D = [{'dog': 1, 'cat': 2, 'elephant': 4}, {'dog': 2, 'run': 5}]
    f = h.transform(D)
    f.toarray()

  def pca(self):
    X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
    pca = PCA(n_components=2)
    pca.fit(X)
    PCA(copy=True, iterated_power='auto', n_components=2, random_state=None,
        svd_solver='auto', tol=0.0, whiten=False)
    print(pca.explained_variance_ratio_)
    print(pca.singular_values_)

  def PP(clf, X_train, X_test, y_train, y_test):
    train_start_time = time.time()
    clf.fit(X_train, y_train)
    print("train time: %.3f sec" % (time.time() - train_start_time))
    test_start_time = time.time()
    y_pred = clf.predict(X_test)
    print("test time: %.3f sec" % (time.time() - test_start_time))
    print ("Accuracy: %.3f" % clf.score(X_test, y_test))
    unique, counts = np.unique(y_pred, return_counts=True)
    print "Absolute reduction: ", counts[0], "/", len(y_test)
    print ("reduction rate: %.3f" % (counts[0] * 1.0 / len(y_test)))



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




