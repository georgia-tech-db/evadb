# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This file implements the inteface for filters

@Jaeho Bang
"""
import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod


class FilterTemplate(metaclass=ABCMeta):

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Train all preprocessing models (if needed)
        :param X: data
        :param y: labels
        :return: None
        """

    @abstractmethod
    def predict(
            self,
            X: np.ndarray,
            premodel_name: str,
            postmodel_name: str) -> np.ndarray:
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

    @abstractmethod
    def getAllStats(self) -> pd.DataFrame:
        """
        This function returns all the statistics acquired after training the preprocessing models and postprocessing models

        :return:
        """
