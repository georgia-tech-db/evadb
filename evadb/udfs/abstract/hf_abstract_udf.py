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
from typing import Any

import pandas as pd

from evadb.catalog.models.udf_catalog import UdfCatalogEntry
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.gpu_compatible import GPUCompatible
from evadb.utils.generic_utils import try_to_import_transformers


class AbstractHFUdf(AbstractUDF, GPUCompatible):
    """
    An abstract class for all HuggingFace models.

    This is implemented using the pipeline API from HuggingFace. pipeline is an
    easy way to use a huggingface model for inference. In EvaDB, we require users
    to mention the task they want to perform for simplicity. A HuggingFace task
    is different from a model(pytorch). There are a large number of models on HuggingFace
    hub that can be used for a particular task. The user can specify the model or a default
    model will be used.

    Refer to https://huggingface.co/transformers/main_classes/pipelines.html for more details
    on pipelines.
    """

    @property
    def name(self) -> str:
        return "GenericHuggingfaceModel"

    def __init__(self, udf_obj: UdfCatalogEntry, device: int = -1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pipeline_args = self.default_pipeline_args
        for entry in udf_obj.metadata:
            if entry.value.isnumeric():
                pipeline_args[entry.key] = int(entry.value)
            else:
                pipeline_args[entry.key] = entry.value
        self.pipeline_args = pipeline_args
        try_to_import_transformers()
        from transformers import pipeline

        self.hf_udf_obj = pipeline(**pipeline_args, device=device)

    def setup(self, *args, **kwargs) -> None:
        super().setup(*args, **kwargs)

    @property
    def default_pipeline_args(self) -> dict:
        """
        Arguments that will be passed to the pipeline by default.
        User provided arguments override the default arguments
        """
        return {}

    def input_formatter(self, inputs: Any):
        """
        Function that formats input from EvaDB format to HuggingFace format for that particular HF model
        """
        return inputs

    def output_formatter(self, outputs: Any):
        """
        Function that formats output from HuggingFace format to EvaDB format (pandas dataframe)
        The output can be in various formats, depending on the model. For example:
            {'text' : 'transcript from video'}
            [[{'score': 0.25, 'label': 'bridge'}, {'score': 0.50, 'label': 'car'}]]
        """
        if isinstance(outputs, dict):
            return pd.DataFrame(outputs, index=[0])
        # PERF: Can improve performance by avoiding redundant list creation
        result_list = []
        if outputs != [[]]:
            for row_output in outputs:
                # account for the case where we have more than one prediction for an input
                if isinstance(row_output, list):
                    row_output = {
                        k: [dic[k] for dic in row_output] for k in row_output[0]
                    }
                result_list.append(row_output)

        result_df = pd.DataFrame(result_list)
        return result_df

    def forward(self, inputs, *args, **kwargs) -> pd.DataFrame:
        hf_input = self.input_formatter(inputs)
        hf_output = self.hf_udf_obj(hf_input, *args, **kwargs)
        evadb_output = self.output_formatter(hf_output)
        return evadb_output

    def to_device(self, device: str) -> GPUCompatible:
        try_to_import_transformers()
        from transformers import pipeline

        self.hf_udf_obj = pipeline(**self.pipeline_args, device=device)
        return self
