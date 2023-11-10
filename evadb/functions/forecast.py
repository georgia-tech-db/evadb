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


import os
import pickle

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
        last_ds: list,
        last_y: list,
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
        self.hypers = None
        self.rmse = None
        if os.path.isfile(model_path + "_rmse"):
            with open(model_path + "_rmse", "r") as f:
                self.rmse = float(f.readline())
                if "arima" in model_name.lower():
                    self.hypers = "p,d,q: " + f.readline()
        self.last_ds = last_ds
        self.last_y = last_y

    def forward(self, data) -> pd.DataFrame:
        log_str = ""
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
                log_str += "\nSUGGESTION: " + self.suggestion_dict[suggestion]

            # Metrics
            if self.rmse is not None:
                log_str += "\nMean normalized RMSE: " + str(self.rmse)
            if self.hypers is not None:
                log_str += "\nHyperparameters: " + self.hypers

            ## Plot figure

            pred_plt = self.last_y + list(
                forecast_df[
                    self.model_name
                    if self.library == "statsforecast"
                    else self.model_name + "-median"
                ]
            )
            pred_plt_lo = self.last_y + list(
                forecast_df[self.model_name + "-lo-" + str(self.conf)]
            )
            pred_plt_hi = self.last_y + list(
                forecast_df[self.model_name + "-hi-" + str(self.conf)]
            )

            plt.plot(pred_plt, label="Prediction")
            plt.fill_between(
                x=range(len(pred_plt)), y1=pred_plt_lo, y2=pred_plt_hi, alpha=0.3
            )
            plt.plot(self.last_y, label="Actual")
            plt.xlabel("Time")
            plt.ylabel("Value")
            xtick_strs = self.last_ds + list(forecast_df["ds"])
            num_to_keep_args = list(
                range(0, len(xtick_strs), int((len(xtick_strs) - 2) / 8))
            ) + [len(xtick_strs) - 1]
            xtick_strs = [
                x if i in num_to_keep_args else "" for i, x in enumerate(xtick_strs)
            ]
            plt.xticks(range(len(pred_plt)), xtick_strs, rotation=85)
            plt.legend()
            plt.tight_layout()

            # convert plt figure to opencv https://copyprogramming.com/howto/convert-matplotlib-figure-to-cv2-image-a-complete-guide-with-examples#converting-matplotlib-figure-to-cv2-image
            # convert figure to canvas
            canvas = plt.get_current_fig_manager().canvas

            # render the canvas
            canvas.draw()

            # convert canvas to image
            img = np.fromstring(canvas.tostring_rgb(), dtype="uint8")
            img = img.reshape(canvas.get_width_height()[::-1] + (3,))

            # convert image to cv2 format
            cv2_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            ## Conver to bytes
            _, buffer = cv2.imencode(".jpg", cv2_img)
            img_bytes = buffer.tobytes()

            ## Add to dataframe as a plot
            forecast_df["plot"] = [img_bytes] + [None] * (len(forecast_df) - 1)

            print(log_str)

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
