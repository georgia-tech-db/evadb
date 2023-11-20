# coding=utf-8
# Copyright 2018-2023 EvaDB
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
import pickle

import pandas as pd

from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.utils.generic_utils import try_to_import_sklearn


class GenericSklearnModel(AbstractFunction):
    @property
    def name(self) -> str:
        return "GenericSklearnModel"

    def setup(self, model_path: str, predict_col: str, **kwargs):
        try_to_import_sklearn()

        self.model = pickle.load(open(model_path, "rb"))
        self.predict_col = predict_col

    def forward(self, frames: pd.DataFrame) -> pd.DataFrame:
        # Do not pass the prediction column in the predict method for sklearn.
        frames.drop([self.predict_col], axis=1, inplace=True)
        predictions = self.model.predict(frames)
        predict_df = pd.DataFrame(predictions)
        # We need to rename the column of the output dataframe. For this we
        # shall rename it to the column name same as that of the predict column
        # passed in the training frames in EVA query.
        predict_df.rename(columns={0: self.predict_col}, inplace=True)
        return predict_df

    def to_device(self, device: str):
        # TODO figure out how to control the GPU for ludwig models
        return self
