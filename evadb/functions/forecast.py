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

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import setup


class ForecastModel(AbstractFunction):
    @property
    def name(self) -> str:
        return "ForecastModel"

    @setup(cacheable=False, function_type="Forecasting", batchable=True)
    def setup(
        self,
        model_name: str,
        model_path: str,
        predict_column_rename: str,
        time_column_rename: str,
        id_column_rename: str,
        horizon: int,
        library: str,
        conf: int,
        data: pd.DataFrame,
    ):
        self.library = library
        if "neuralforecast" in self.library:
            from neuralforecast import NeuralForecast

            loaded_model = NeuralForecast.load(path=model_path)
            self.model_name = model_name[4:] if "Auto" in model_name else model_name
        else:
            with open(model_path, "rb") as f:
                loaded_model = pickle.load(f)
            self.model_name = model_name
        self.model = loaded_model
        self.predict_column_rename = predict_column_rename
        self.time_column_rename = time_column_rename
        self.id_column_rename = id_column_rename
        self.horizon = int(horizon)
        self.library = library
        self.suggestion_dict = {
            1: "Predictions are flat. Consider using LIBRARY 'neuralforecast' for more accrate predictions.",
        }
        self.conf = conf
        self.training_data = pd.read_json(data, orient="split")
        self.training_data.ds = pd.to_datetime(self.training_data.ds)

    def forward(self, data) -> pd.DataFrame:
        if self.library == "statsforecast":
            forecast_df = self.model.predict(
                h=self.horizon, level=[self.conf]
            ).reset_index()
        else:
            forecast_df = self.model.predict().reset_index()

        # Feedback
        if len(data) == 0 or list(list(data.iloc[0]))[0] is True:
            # Suggestions
            suggestion_list = []
            # 1: Flat predictions
            if self.library == "statsforecast":
                for type_here in forecast_df["unique_id"].unique():
                    if (
                        forecast_df.loc[forecast_df["unique_id"] == type_here][
                            self.model_name
                        ].nunique()
                        == 1
                    ):
                        suggestion_list.append(1)

            for suggestion in set(suggestion_list):
                print("\nSUGGESTION: " + self.suggestion_dict[suggestion])

            # Metrics
            if self.library == "statsforecast":
                crossvalidation_df = self.model.cross_validation(
                    df=self.training_data[["ds", "y", "unique_id"]],
                    h=self.horizon,
                    step_size=24,
                    n_windows=1,
                ).reset_index()
                rmses = []
                for uid in crossvalidation_df.unique_id.unique():
                    crossvalidation_df_here = crossvalidation_df[
                        crossvalidation_df.unique_id == uid
                    ]
                    rmses.append(
                        mean_squared_error(
                            crossvalidation_df_here.y,
                            crossvalidation_df_here[self.model_name],
                            squared=False,
                        )
                        / np.mean(crossvalidation_df_here.y)
                    )
                print("\nMean normalized RMSE: " + str(np.mean(rmses)))

        forecast_df = forecast_df.rename(
            columns={
                "unique_id": self.id_column_rename,
                "ds": self.time_column_rename,
                self.model_name
                if self.library == "statsforecast"
                else self.model_name + "-median": self.predict_column_rename,
                self.model_name
                + "-lo-"
                + str(self.conf): self.predict_column_rename
                + "-lo",
                self.model_name
                + "-hi-"
                + str(self.conf): self.predict_column_rename
                + "-hi",
            }
        )[: self.horizon * forecast_df["unique_id"].nunique()]
        return forecast_df
