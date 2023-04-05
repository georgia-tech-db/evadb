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
import tempfile
from typing import Dict, List, Type, Union

import cv2
import numpy as np
from PIL import Image, ImageDraw
from transformers import Pipeline, pipeline
from transformers.pipelines import SUPPORTED_TASKS

from eva.catalog.catalog_type import ColumnType, NdArrayType
from eva.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from eva.catalog.models.udf_metadata_catalog import UdfMetadataCatalogEntry

UNSUPPORTED_TASKS = [
    "feature-extraction",
    "token-classification",
    "question-answering",
    "visual-question-answering",
    "document-question-answering",
    "table-question-answering",
    "conversational",
    "fill-mask",
    "zero-shot-classification",
    "zero-shot-image-classification",
    "zero-shot-object-detection",
    "zero-shot-audio-classification",
]


def run_pipe_through_text(pipe: Pipeline):
    input = "The cat is on the mat"
    return pipe(input)


def run_pipe_through_image(pipe: Pipeline):
    width, height = 224, 224
    dummy_image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(dummy_image)

    circle_radius = min(width, height) // 4
    circle_center = (width // 2, height // 2)
    circle_bbox = (
        circle_center[0] - circle_radius,
        circle_center[1] - circle_radius,
        circle_center[0] + circle_radius,
        circle_center[1] + circle_radius,
    )
    draw.ellipse(circle_bbox, fill="yellow")

    return pipe(dummy_image)


def run_pipe_through_audio(pipe: Pipeline):
    duration_ms, sample_rate = 1000, 16000
    num_samples = int(duration_ms * sample_rate / 1000)
    silent_data = np.random.rand(num_samples)
    return pipe(silent_data)


def run_pipe_through_video(pipe: Pipeline):
    width, height, fps, duration_sec = 224, 224, 30, 1
    num_frames = fps * duration_sec
    blank_frame = np.zeros((height, width, 3), dtype=np.uint8)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(temp_file.name, fourcc, fps, (width, height))

        for _ in range(num_frames):
            video_writer.write(blank_frame)

        video_writer.release()
        output = pipe(temp_file.name)
    return output


def run_pipe_through_multi_modal_text_image(pipe: Pipeline):
    width, height = 224, 224
    image_input = Image.new("RGB", (width, height), "white")
    text_input = "This is a dummy text input"
    return pipe(image=image_input, text=text_input)


def infer_output_type(**pipeline_args):
    """
    Infer the output type of a pipeline based on the task type.
    Note: The below code is flaky and depends on the version of transformers.
    It also hard-codes the type assignment to certain tasks.
    """
    if "task" not in pipeline_args:
        raise Exception("Task Not Found In Model Definition")
    task = pipeline_args["task"]
    if task in UNSUPPORTED_TASKS:
        raise Exception(f"HuggingFace task:{task} not supported in EVA currently")

    task_input = SUPPORTED_TASKS.get(task, {}).get("type", None)
    if task_input is None:
        raise Exception("Task Type Could Not Be Inferred")

    pipe = pipeline(**pipeline_args)
    if task_input == "text":
        output = run_pipe_through_text(pipe)
    elif (
        task_input == "image"
        or task == "image-segmentation"
        or task == "image-to-text"
        or task == "object-detection"
    ):
        output = run_pipe_through_image(pipe)
    elif task_input == "audio" or (
        task_input == "multimodal" and ("audio" in task or "speech" in task)
    ):
        output = run_pipe_through_audio(pipe)
    elif task_input == "video":
        output = run_pipe_through_video(pipe)
    elif task_input == "multimodal":
        output = run_pipe_through_multi_modal_text_image(pipe)

    task_outputs = {}
    if isinstance(output, list):
        sample_out = output[0]
    else:
        sample_out = output
    for key, value in sample_out.items():
        task_outputs[key] = type(value)

    return task_input, task_outputs


def io_entry_for_inputs(udf_name: str, udf_input: Union[str, List]):
    """
    Generates the IO Catalog Entry for the input
    Input is one of ["text", "image", "audio", "video", "multimodal"]
    """
    if isinstance(udf_input, str):
        udf_input = [udf_input]
    inputs = []
    for input_type in udf_input:
        array_type = NdArrayType.ANYTYPE
        if input_type == "text":
            array_type = NdArrayType.STR
        elif input_type == "image" or udf_input == "audio":
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
    udf_input, udf_output = infer_output_type(**pipeline_args)
    annotated_inputs = io_entry_for_inputs(udf_name, udf_input)
    annotated_outputs = io_entry_for_outputs(udf_output)
    return annotated_inputs + annotated_outputs
