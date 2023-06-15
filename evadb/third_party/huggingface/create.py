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
from typing import Dict, List, Type, Union

import numpy as np

from evadb.catalog.catalog_type import ColumnType, NdArrayType
from evadb.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from evadb.catalog.models.udf_metadata_catalog import UdfMetadataCatalogEntry
from evadb.third_party.huggingface.model import (
    ASRHFModel,
    AudioHFModel,
    HFInputTypes,
    ImageHFModel,
    TextHFModel,
)
from evadb.utils.generic_utils import try_to_import_transformers

"""
We currently support the following tasks from HuggingFace.
Each task is mapped to the type of input it expects.
"""
INPUT_TYPE_FOR_SUPPORTED_TASKS = {
    "audio-classification": HFInputTypes.AUDIO,
    "automatic-speech-recognition": HFInputTypes.AUDIO,
    "text-classification": HFInputTypes.TEXT,
    "summarization": HFInputTypes.TEXT,
    "translation": HFInputTypes.TEXT,
    "text2text-generation": HFInputTypes.TEXT,
    "text-generation": HFInputTypes.TEXT,
    "ner": HFInputTypes.TEXT,
    "image-classification": HFInputTypes.IMAGE,
    "image-segmentation": HFInputTypes.IMAGE,
    "image-to-text": HFInputTypes.IMAGE,
    "object-detection": HFInputTypes.IMAGE,
    "depth-estimation": HFInputTypes.IMAGE,
}

MODEL_FOR_TASK = {
    "audio-classification": AudioHFModel,
    "automatic-speech-recognition": ASRHFModel,
    "text-classification": TextHFModel,
    "summarization": TextHFModel,
    "translation": TextHFModel,
    "text2text-generation": TextHFModel,
    "text-generation": TextHFModel,
    "ner": TextHFModel,
    "image-classification": ImageHFModel,
    "image-segmentation": ImageHFModel,
    "image-to-text": ImageHFModel,
    "object-detection": ImageHFModel,
    "depth-estimation": ImageHFModel,
}


def sample_text():
    return "My name is Sarah and I live in London"


def sample_image():
    from PIL import Image, ImageDraw

    width, height = 224, 224
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    circle_radius = min(width, height) // 4
    circle_center = (width // 2, height // 2)
    circle_bbox = (
        circle_center[0] - circle_radius,
        circle_center[1] - circle_radius,
        circle_center[0] + circle_radius,
        circle_center[1] + circle_radius,
    )
    draw.ellipse(circle_bbox, fill="yellow")
    return image


def sample_audio():
    duration_ms, sample_rate = 1000, 16000
    num_samples = int(duration_ms * sample_rate / 1000)
    audio_data = np.random.rand(num_samples)
    return audio_data


def gen_sample_input(input_type: HFInputTypes):
    if input_type == HFInputTypes.TEXT:
        return sample_text()
    elif input_type == HFInputTypes.IMAGE:
        return sample_image()
    elif input_type == HFInputTypes.AUDIO:
        return sample_audio()
    assert False, "Invalid Input Type for UDF"


def infer_output_name_and_type(**pipeline_args):
    """
    Infer the name and type for each output of the HuggingFace UDF
    """
    assert "task" in pipeline_args, "Task Not Found In Model Definition"
    task = pipeline_args["task"]
    assert (
        task in INPUT_TYPE_FOR_SUPPORTED_TASKS
    ), f"Task {task} not supported in EvaDB currently"

    # Construct the pipeline
    try_to_import_transformers()
    from transformers import pipeline

    pipe = pipeline(**pipeline_args)

    # Run the pipeline through a dummy input to get a sample output
    input_type = INPUT_TYPE_FOR_SUPPORTED_TASKS[task]
    model_input = gen_sample_input(input_type)
    model_output = pipe(model_input)

    # Get a dictionary of output names and types from the output
    output_types = {}
    if isinstance(model_output, list):
        sample_out = model_output[0]
    else:
        sample_out = model_output

    for key, value in sample_out.items():
        output_types[key] = type(value)

    return input_type, output_types


def io_entry_for_inputs(udf_name: str, udf_input: Union[str, List]):
    """
    Generates the IO Catalog Entry for the inputs to HF UDFs
    Input is one of ["text", "image", "audio", "video", "multimodal"]
    """
    if isinstance(udf_input, HFInputTypes):
        udf_input = [udf_input]
    inputs = []
    for input_type in udf_input:
        array_type = NdArrayType.ANYTYPE
        if input_type == HFInputTypes.TEXT:
            array_type = NdArrayType.STR
        elif input_type == HFInputTypes.IMAGE or udf_input == HFInputTypes.AUDIO:
            array_type = NdArrayType.FLOAT32
        inputs.append(
            UdfIOCatalogEntry(
                name=f"{udf_name}_{input_type}",
                type=ColumnType.NDARRAY,
                is_nullable=False,
                array_type=array_type,
                is_input=True,
            )
        )
    return inputs


def ptype_to_ndarray_type(col_type: type):
    """
    Helper function that maps python types to ndarray types
    """
    if col_type == str:
        return NdArrayType.STR
    elif col_type == float:
        return NdArrayType.FLOAT32
    else:
        return NdArrayType.ANYTYPE


def io_entry_for_outputs(udf_outputs: Dict[str, Type]):
    """
    Generates the IO Catalog Entry for the output
    """
    outputs = []
    for col_name, col_type in udf_outputs.items():
        outputs.append(
            UdfIOCatalogEntry(
                name=col_name,
                type=ColumnType.NDARRAY,
                array_type=ptype_to_ndarray_type(col_type),
                is_input=False,
            )
        )
    return outputs


def gen_hf_io_catalog_entries(udf_name: str, metadata: List[UdfMetadataCatalogEntry]):
    """
    Generates IO Catalog Entries for a HuggingFace UDF.
    The attributes of the huggingface model can be extracted from metadata.
    """
    pipeline_args = {arg.key: arg.value for arg in metadata}
    udf_input, udf_output = infer_output_name_and_type(**pipeline_args)
    annotated_inputs = io_entry_for_inputs(udf_name, udf_input)
    annotated_outputs = io_entry_for_outputs(udf_output)
    return annotated_inputs + annotated_outputs
