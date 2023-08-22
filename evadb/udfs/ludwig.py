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
import pandas as pd

from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.utils.generic_utils import try_to_import_ludwig


class GenericLudwigModel(AbstractUDF):
    @property
    def name(self) -> str:
        return "GenericLudwigModel"

    def setup(self, model_path: str, **kwargs):
        try_to_import_ludwig()
        from ludwig.api import LudwigModel

        self.model = LudwigModel.load(model_path)

    def forward(self, frames: pd.DataFrame) -> pd.DataFrame:
        predictions, _ = self.model.predict(frames, return_type=pd.DataFrame)
        return predictions

    def to_device(self, device: str):
        # TODO figure out how to control the GPU for ludwig models
        return self
