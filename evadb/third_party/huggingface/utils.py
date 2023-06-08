# coding=utf-8
# Copyright 2018-2023 EVA
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

import ast
from typing import List

from evadb.catalog.models.udf_metadata_catalog import UdfMetadataCatalogEntry


def literal_eval_with_default(value: str):
    """
    Helper function to evaluate a string as a python literal.
    If the string is not a valid python literal, return the string itself.
    """
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def split_args_from_metadata(metadata: List[UdfMetadataCatalogEntry]):
    """
    Split the metadata into udf definition args and udf inference args.
    Inference args are prefixed with INFERENCE_.
    """
    definition_args = {}
    inference_args = {}
    for arg in metadata:
        key, value = arg.key, literal_eval_with_default(arg.value)
        if arg.key.startswith("INFERENCE_"):
            key = key.replace("INFERENCE_", "")
            inference_args[key] = value
        else:
            definition_args[key] = value
    return definition_args, inference_args
