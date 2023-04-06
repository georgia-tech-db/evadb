# coding=utf-8
# Copyright 2018-2022 EVA
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
from typing import Any

import pandas as pd
from transformers import pipeline

from eva.catalog.models.udf_catalog import UdfCatalogEntry
from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.udfs.gpu_compatible import GPUCompatible


class AbstractHFUdf(AbstractUDF, GPUCompatible):
    """
    An abstract class for all HuggingFace models.
    This class performs the necessary data transformations between EVA and HuggingFace.
    """

    @property
    def name(self) -> str:
        return "GenericHuggingfaceModel"

    def setup(
        self, udf_obj: UdfCatalogEntry, device: int = -1, *args, **kwargs
    ) -> None:
        pipeline_args = {entry.key: entry.value for entry in udf_obj.metadata}
        self.hf_udf_obj = pipeline(**pipeline_args, device=device)

    def input_formatter(self, inputs: Any):
        """
        Function that formats input from EVA format to HuggingFace format for that particular HF model
        """
        return inputs

    def output_formatter(self, outputs: Any):
        """
        Function that formats output from HuggingFace format to EVA format (pandas dataframe)
        """
        # PERF: Can improve performance by avoiding redundant list creation
        result_list = []
        for row_output in outputs:
            # account for the case where we have more than one prediction for an input
            if isinstance(row_output, list):
                row_output = {k: [dic[k] for dic in row_output] for k in row_output[0]}
            result_list.append(row_output)
        result_df = pd.DataFrame(result_list)
        return result_df

    def forward(self, inputs, *args, **kwargs) -> None:
        hf_input = self.input_formatter(inputs)
        hf_output = self.hf_udf_obj(hf_input, *args, **kwargs)
        eva_output = self.output_formatter(hf_output)
        return eva_output

    def to_device(self, device: str) -> GPUCompatible:
        pass
