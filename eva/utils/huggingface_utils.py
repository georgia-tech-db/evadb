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
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd
from PIL import Image
from transformers import pipeline
from transformers.pipelines import (
    ImageClassificationPipeline,
    ObjectDetectionPipeline,
    TextClassificationPipeline,
)

from eva.catalog.models.udf_catalog import UdfCatalogEntry


def image_data_preprocesser(images):
    frames_list = images.values.tolist()
    frames = np.array(frames_list)
    frames = np.vstack(frames)
    images = [Image.fromarray(row) for row in frames]
    return images


def data_postprocesser(model_output):
    outcome = pd.DataFrame()
    for i in range(len(model_output)):
        outcome = outcome.append(model_output[i], ignore_index=True)
    return outcome


class CustomImageClassification(ImageClassificationPipeline):
    def __call__(self, images, **kwargs):
        images = image_data_preprocesser(images)
        model_output = super().__call__(images, **kwargs)
        outcome = data_postprocesser(model_output)
        return outcome


class CustomObjectDetection(ObjectDetectionPipeline):
    def __call__(self, images, **kwargs):
        images = image_data_preprocesser(images)
        model_output = super().__call__(images, **kwargs)
        outcome = data_postprocesser(model_output)
        return outcome


class CustomTextClassification(TextClassificationPipeline):
    def __call__(self, texts, **kwargs):
        texts = texts.values.flatten().tolist()
        model_output = super().__call__(texts, **kwargs)
        outcome = data_postprocesser(model_output)
        return outcome


task_class_mapping = {
    "image-classification": CustomImageClassification,
    "object-detection": CustomObjectDetection,
    "text-classification": CustomTextClassification,
}


def bind_hf_func_from_udf(udf_obj: UdfCatalogEntry):
    """
    Generate and return pipeline function from UdfCatalogEntry
    """
    default_args = {
        "task": "text-classification",
    }
    for metadata in udf_obj.metadata:
        key = metadata.key.lower()
        default_args[key] = metadata.value
    return lambda: pipeline(
        **default_args, pipeline_class=task_class_mapping.get(default_args["task"])
    )
