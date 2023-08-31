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
import pickle


class ForecastModel(AbstractUDF):
    @property
    def name(self) -> str:
        return "ForecastModel"

    @setup(cacheable=False, udf_type="Forecasting", batchable=True)
    def setup(self, model_name: str, model_path: str):
        try_to_import_forecast()
        from statsforecast import StatsForecast
        from statsforecast.models import AutoARIMA, AutoCES, AutoETS, AutoTheta

        f = open(model_path, "rb")
        loaded_model = pickle.load(f)
        f.close()
        self.model = loaded_model
        self.model_name = model_name


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
        horizon = list(data.iloc[:,-1])[0]
        assert (
                type(horizon) == int
            ), f"Forecast UDF expects integral horizon in parameter."
        forecast_df = self.model.predict(h=horizon)
        forecast_df = forecast_df.rename(columns={self.model_name: "y"})
        return pd.DataFrame(
            forecast_df,
            columns=[
                "y",
            ],
        )
