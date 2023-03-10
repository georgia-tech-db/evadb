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


from eva.utils.errors import TypeException
from eva.io_descriptors.eva_arguments import EvaArgument

# decorator for the setup function. It will be used to set the cache, batching and
# udf_type parameters in the catalog
def setup(use_cache: bool, udf_type: str, batch: bool):
    def inner_fn(arg_fn):
        print("Cache is set: ", use_cache)
        print("batching is set: ", batch)

        def wrapper(*args, **kwargs):

            # TODO set the batch and caching parameters. update in catalog

            # calling the setup function defined by the user inside the udf implementation
            arg_fn(*args, **kwargs)

        tags = {}
        tags["cache"] = use_cache
        tags["udf_type"] = udf_type
        tags["batching"] = batch
        wrapper.tags = tags
        return wrapper

    return inner_fn


def forward(input_signature: EvaArgument, output_signature: EvaArgument):
    """decorator for the forward function. This will validate the shape and data type of inputs and outputs from the UDF.

    Additionally if the output is a Pandas dataframe, then it will check if the column names are matching.
    Args:
        input_signature (EvaArgument): Constraints for the input.
            shape : shape should be in the format (batch_size, nos_of_channels, width, height)
        output_signature (EvaArgument): _description_
    """

    def inner_fn(arg_fn):
        def wrapper(*args):

            frames = args[1]

            # check shape of input
            if input_signature:
                if (input_signature.is_shape_defined) and (
                    not (input_signature.check_shape(frames))):
                    msg = "Shape mismatch of input parameter. "
                    raise TypeException(msg)

                # check type of input
                if (input_signature.is_dtype_defined) and (
                    not (input_signature.check_type(frames))
                ):
                    msg = "Datatype mismatch of Input parameter. "
                    raise TypeException(msg)

            # first argument is self and second is frames.
            output = arg_fn(args[0], frames)

            # check output type
            if output_signature:
                # check shape
                if (output_signature.is_shape_defined) and (
                    not (output_signature.check_shape(output))
                ):
                    msg = "Shape mismatch of Output parameter. "
                    raise TypeException(msg)

                # check type of output
                if (output_signature.is_dtype_defined) and (
                    not (output_signature.check_type(output))
                ):
                    msg = "Datatype mismatch of Output parameter. "
                    raise TypeException(msg)

                # check if the column headers are matching
                if output_signature.is_output_columns_set():
                    if not output_signature.check_column_names(output):
                        raise TypeException("Column header names are not matching")

            return output

        tags = {}
        tags["input"] = input_signature
        tags["output"] = output_signature
        wrapper.tags = tags
        return wrapper

    return inner_fn

