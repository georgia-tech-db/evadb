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
from eva.catalog.catalog_type import NdArrayType
from eva.catalog.models.udf_catalog import UdfCatalogEntry
from eva.third_party.huggingface.model import ImageHFModel, TextHFModel


def assign_hf_udf(udf_obj: UdfCatalogEntry):
    """
    Assigns the correct HF Model to the UDF. The model assigned depends on
    the type of input the UDF expects. This is done so that we can
    process the input correctly before passing it to the HF model.
    """
    inputs = udf_obj.args

    # NOTE: Currently, we only support models that require a single input.
    assert len(inputs) == 1, "Only single input models are supported."
    input_type = inputs[0].array_type

    # By default, we assume that the input is an image.
    model_class = ImageHFModel

    # If the input is a string, assign a TextHFModel.
    if input_type == NdArrayType.STR:
        model_class = TextHFModel

    return lambda: model_class(udf_obj)
