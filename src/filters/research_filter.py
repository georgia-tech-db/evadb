"""
This file is composed of the composing preliminary and post filtering techniques.
Main use of this code is for research purposes - eva_storage

@Jaeho Bang
"""

import numpy as np
import pandas as pd

from copy import deepcopy
from src.filters import FilterTemplate
from src.filters.models.ml_randomforest import MLRandomForest
from src.filters import MLSVM
from src.filters import MLMLP


# Meant to be a black box for trying all models available and returning statistics and model for
# the query optimizer to choose for a given query

"""
Each Filter object considers 1 specific query. Either the query optimizer or the pipeline needs to manage a diction of Filters

"""


class FilterResearch(FilterTemplate):
    def __init__(self):

        """
        self.pre_models = {'pca': pca_model_instance, 'hashing': hashing_model_instance, 'sampling': sampling_model_instance}
        self.post_models = {'rf': rf_instance, 'svm':svm_instance, 'dnn':dnn_instance}
        self.all_models = {'rf': {'pca': (pca_model_instance, rf_instance_for_pca),
                                  'hashing': (hashing_instance, rf_instance_for_hashing),
                                  'sampling': (sampling_instance, rf_instance_for_sampling),
                                  },
                           'svm': {'pca': (pca_model_instance, svm_instance_for_pca),.....
                           }

        -> post models that doesn't use any pre processing models are saved in self.post_models
        -> post models that do use pre processing models are saved in self.all_models
        -> in this base class, we take care of those things, so no worries!
        """

        self.pre_models = {}
        self.post_models = {}
        self.all_models = {}

        rf = MLRandomForest()
        svm = MLSVM()
        dnn = MLMLP()
        self.addPostModel('rf', rf)
        self.addPostModel('svm', svm)
        self.addPostModel('dnn', dnn)

    def updateModelStatus(self):
        """
        Add combinations of models
        Function should be called whenever add*Model() is called

        :return: None
        """
        post_model_names = self.post_models.keys()
        pre_model_names = self.pre_models.keys()
        for post_model_name in post_model_names:
            if post_model_name not in self.all_models:
                self.all_models[post_model_name] = {}
            for pre_model_name in pre_model_names:
                if pre_model_name not in self.all_models[post_model_name]:
                    self.all_models[post_model_name][pre_model_name] = (self.pre_models[pre_model_name],
                                                                        deepcopy(self.post_models[post_model_name]))

    def addPreModel(self, model_name, model):
        """
        Add preprocessing machine learning/statistical models such as PCA, Sampling, etc
        :param model_name: name of model must be string
        :param model: model
        :return: None
        """
        self.pre_models[model_name] = model
        self.updateModelStatus()

    def addPostModel(self, model_name, model):
        """
        Add postprocessing machine learning/statistical models such as SVM, DNN, random forest, etc
        :param model_name: name of model must be string
        :param model: model
        :return: None
        """
        self.post_models[model_name] = model
        self.updateModelStatus()

    def deletePreModel(self, pre_model_name):
        """
        Delete preprocessing model from models dictionary
        :param model_name: name of model
        :return: None
        """
        if pre_model_name in self.pre_models.keys():
            self.pre_models.pop(pre_model_name)

            for post_model_name in self.all_models.keys():
                if pre_model_name in self.all_models[post_model_name]:
                    self.all_models[post_model_name].pop(pre_model_name)
        else:
            print("model name not found in pre model dictionary..")
            print("  ", self.pre_models.keys(), "are available")
        return

    def deletePostModel(self, post_model_name):
        """
        Delete postprocessing model from models dictionary
        :param model_name: name of model
        :return: None
        """
        if post_model_name in self.post_models.keys():
            self.post_models.pop(post_model_name)
            if post_model_name in self.all_models.keys():
                self.all_models.pop(post_model_name)
        else:
            print("model name not found in post model dictionary..")
            print("  ", self.post_models.keys(), "are available")

    def train(self, X: np.ndarray, y: np.ndarray):
        for post_model_name, post_model in self.post_models.items():
            post_model.train(X, y)

        for pre_model_name, pre_model in self.pre_models.items():
            pre_model.train(X, y)

        for post_model_names, internal_dict in self.all_models.items():
            for pre_model_names, pre_post_instance_pair in internal_dict.items():
                pre_model, post_model = pre_post_instance_pair
                X_transform = pre_model.predict(X)
                post_model.train(X_transform)

    def predict(self, X: np.ndarray, pre_model_name: str = None, post_model_name: str = None) -> np.ndarray:
        pre_model_names = self.pre_models.keys()
        post_model_names = self.post_models.keys()

        ## If we haven't found the post model, there is no prediction to be done
        ## so we must raise an error
        if post_model_name is None:
            print("No Post Model is found.")
            print("  Available:", post_model_names)
            return np.array([])
        elif post_model_name not in self.post_models.keys():
            print("Given Post Model is found.")
            print("  Given:", post_model_name)
            print("  Available:", post_model_names)
            return np.array([])

        if pre_model_name is None:
            return self.post_models[post_model_name].predict(X)
        elif pre_model_name not in pre_model_names:
            print("Given Pre Model is not found.")
            print("  Given:", pre_model_name)
            print("  Available:", pre_model_names)
            print("  Using only given post model for prediction...")
            return self.post_models[post_model_name].predict(X)
        else:
            pre_model, post_model = self.all_models[post_model_name][pre_model_name]
            X_transform = pre_model.predict(X)
            return post_model.predict(X_transform)

    def getAllStats(self):
        """
        TODO!!!!
        will need to organize the stats in a panda format where rows correspond to models and cols correspond to RCA values
        One thing to think about is to whether to separate the stats between preprocessing models or post processing models....


        Header(columns) would be [Name, R, C, A]
        The name of pre_model, post_model pair will be separated using semi-colon(;)
        However, if no pre_model is used, only the name of the post_model will appear
        ex1) if 'pca' and 'svm' -> 'pca;svm'
        ex2) if 'svm' -> 'svm'

        :return: dataframe
        """

        name_col = []
        c_col = []
        r_col = []
        a_col = []
        for post_model_name, post_model in self.post_models.items():
            name_col.append(post_model_name)
            c_col.append(getattr(post_model, 'C'))
            r_col.append(getattr(post_model, 'R'))
            a_col.append(getattr(post_model, 'A'))

        for post_model_name, internal_dict in self.all_models.items():
            for pre_model_name, model_pair in internal_dict.items():
                pre_model, post_model = model_pair
                model_name = pre_model_name + ';' + post_model_name
                name_col.append(model_name)
                c_col.append(getattr(pre_model, 'C') + getattr(post_model, 'C'))
                r_col.append(getattr(post_model, 'R'))
                a_col.append(getattr(post_model, 'A'))

        assert (len(name_col) == len(c_col))
        assert (len(name_col) == len(r_col))
        assert (len(name_col) == len(a_col))

        data = {'Name': name_col, 'C': c_col, 'R': r_col, 'A': a_col}
        # Create DataFrame
        df = pd.DataFrame(data)

        return df


if __name__ == "__main__":
    filter = FilterResearch()

    X = np.random.random([100, 30, 30, 3])
    y = np.random.random([100])
    y *= 10
    y = y.astype(np.int32)

    division = int(X.shape[0] * 0.8)
    X_train = X[:division]
    X_test = X[division:]
    y_iscar_train = y[:division]
    y_iscar_test = y[division:]

    filter.train(X_train, y_iscar_train)
    print("filter finished training!")
    y_iscar_hat = filter.predict(X_test, post_model_name='rf')
    print("filter finished prediction!")
    stats = filter.getAllStats()
    print(stats)
    print("filter got all stats")








