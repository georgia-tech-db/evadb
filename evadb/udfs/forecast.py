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

import pandas as pd
from retry import retry
import pudb
from evadb.catalog.catalog_type import NdArrayType
from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_openai, try_to_import_forecast

class ForecastModel(AbstractUDF):
    @property
    def name(self) -> str:
        return "ForecastModel"

    @setup(cacheable=False, udf_type="Forecasting", batchable=True)
    def setup(self, model: str = "AutoARIMA", frequency: str = "M", horizon: int = 12):
        try_to_import_forecast()
        from statsforecast import StatsForecast
        from statsforecast.models import AutoARIMA, AutoCES, AutoETS, AutoTheta
        self.model_name = model
        self.model_dict = {
            "AutoARIMA": AutoARIMA,
            "AutoCES": AutoCES,
            "AutoETS": AutoETS,
            "AutoTheta": AutoTheta,
        }

        season_dict = {  # https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
            "H": 24,
            "M": 12,
            "Q": 4,
            "SM": 24,
            "BM": 12,
            "BMS": 12,
            "BQ": 4,
            "BH": 24,
            }
        # pu.db
        new_freq = frequency.split("-")[0] if "-" in frequency else frequency  # shortens longer frequencies like Q-DEC
        season_length = season_dict[new_freq] if new_freq in season_dict else 1
        self.model = StatsForecast([self.model_dict[self.model_name](season_length=season_length)], freq=new_freq)
        self.data_memory = pd.DataFrame()
        self.horizon = horizon


    @forward(
        input_signatures=[],
        output_signatures=[
            PandasDataframe(
                columns=["y"],
                column_types=[
                    NdArrayType.FLOAT32,
                ],
                column_shapes=[(None,)],
            )
        ],
    )
    def forward(self, data) -> pd.DataFrame:
        if not self.data_memory.equals(data):
            self.data_memory = data
            self.model.fit(data)
        forecast_df = self.model.predict(h=self.horizon)
        forecast_df = forecast_df.rename(columns={self.model_name: "y"})
        return pd.DataFrame(
            forecast_df,
            columns=[
                "y",
            ],
        )
