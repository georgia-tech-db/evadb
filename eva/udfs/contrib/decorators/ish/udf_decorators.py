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

import warnings

import torch
import yolov5

from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument
from eva.udfs.contrib.decorators.ish.io_descriptors.type_exception import TypeException


def setup(use_cache: bool, batch: bool):
    def inner_fn(arg_fn):
        print("Cache is set: ", use_cache)
        print("batching is set: ", batch)

        def wrapper(*args, **kwargs):

            # TODO set the batch and caching parameters.

            arg_fn(*args, **kwargs)

        return wrapper

    return inner_fn


def forward(input_signature: EvaArgument, output_signature: EvaArgument):
    def inner_fn(arg_fn):
        def wrapper(*args):

            frames = args[1]

            # check type of input
            if not (input_signature.check_type(frames)):
                raise TypeException(
                    "Expected %s but received %s"
                    % (input_signature.name(), type(args[0]))
                )
            else:
                print("correct input")

            # check shape of input
            if input_signature:
                if not (input_signature.check_shape(frames)):
                    raise TypeException("Mismatch in shape of array.")

            # first argument is self and second is frames.
            output = arg_fn(args[0], frames)

            # check output type
            if not (output_signature.check_type(output)):
                raise TypeException(
                    "Expected %s as output but received %s"
                    % (output_signature.name(), type(output))
                )

            # check if the column headers are matching
            if output_signature.is_output_columns_set():
                if not output_signature.check_column_names(output):
                    warnings.warn("Column header names are not matching")

            return output

        return wrapper

    return inner_fn
