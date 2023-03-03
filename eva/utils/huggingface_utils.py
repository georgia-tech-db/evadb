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
from typing import Any, Dict, Union, List, List


from eva.catalog.models.udf_catalog import UdfCatalogEntry
from transformers import pipeline
from transformers.pipelines import ImageClassificationPipeline, ObjectDetectionPipeline
from PIL import Image
import numpy as np
import pandas as pd


class CustomImageClassification(ImageClassificationPipeline):
    def __call__(self, images, **kwargs):
        frames_list = images.values.tolist()
        frames = np.array(frames_list)
        frames = np.vstack(frames)
        images = [Image.fromarray(row) for row in frames][:2]
        model_output = super().__call__(images, **kwargs)
        outcome = pd.DataFrame() 
        for i in range(len(model_output)):
            outcome = outcome.append(model_output[i], ignore_index=True)
        return outcome
    
class CustomObjectDetection(ObjectDetectionPipeline):
    def __call__(self, images, **kwargs):
        frames_list = images.values.tolist()
        frames = np.array(frames_list)
        frames = np.vstack(frames)
        images = [Image.fromarray(row) for row in frames][:2]
        model_output = super().__call__(images, **kwargs)
        outcome = pd.DataFrame() 
        for i in range(len(model_output)):
            outcome = outcome.append(model_output[i], ignore_index=True)
        return outcome

task_class_mapping = {'image-classification': CustomImageClassification, 'object-detection': CustomObjectDetection}


def bind_hf_func_from_udf(udf_obj: UdfCatalogEntry):
    """
    Generate and return pipeline function from UdfCatalogEntry 
    """
    default_args = {'task' : 'text-classification', }
    for metadata in udf_obj.metadata:
        key = metadata.key.lower()
        default_args[key] = metadata.value
    return  lambda : pipeline(**default_args, pipeline_class=task_class_mapping.get(default_args['task']))
