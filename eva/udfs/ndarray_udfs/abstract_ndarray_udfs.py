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
from abc import ABCMeta, abstractmethod
import pandas as pd


class AbstractNdarrayUDF(metaclass=ABCMeta):
    """
    Abstract class for UDFs. All the UDFs which perform operation on Ndarrays
    should inherit this class
    """

    def __init__(self):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def exec(self, inp: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        All the UDFs need to implement exec function.
        Arguments:
            input (pd.DataFrame): Input batch on which the operator needs to
                be applied
        Returns:
            pd.DataFrame: The outcome batch after applying the operator
        """

    def __call__(self, *args, **kwargs):
        return self.exec(*args, **kwargs)
