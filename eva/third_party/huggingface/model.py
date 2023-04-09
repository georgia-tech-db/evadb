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

import numpy as np
from PIL import Image

from eva.udfs.abstract.hf_abstract_udf import AbstractHFUdf
from eva.utils.generic_utils import EVAEnum


class HFInputTypes(EVAEnum):
    TEXT  # noqa: F821
    IMAGE  # noqa: F821
    AUDIO  # noqa: F821
    VIDEO  # noqa: F821
    MULTIMODAL_TEXT_IMAGE  # noqa: F821


class TextHFModel(AbstractHFUdf):
    """
    Base Model for all HF Models that take in text as input
    """

    def input_formatter(self, inputs: Any):
        return inputs.values.flatten().tolist()


class ImageHFModel(AbstractHFUdf):
    """
    Base Model for all HF Models that take in images as input
    """

    def input_formatter(self, inputs: Any):
        frames_list = inputs.values.tolist()
        frames = np.vstack(frames_list)
        images = [Image.fromarray(row) for row in frames]
        return images
