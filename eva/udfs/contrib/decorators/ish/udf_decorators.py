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


from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument
from eva.utils.errors import TypeException


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
                if not (input_signature.check_shape(frames)):
                    try:
                        frames = input_signature.reshape(frames)
                    except TypeException as e:
                        msg = "Shape mismatch of Input parameter. " + str(e)
                        raise TypeException(msg)

                # check type of input
                if not (input_signature.check_type(frames)):
                    try:
                        frames = input_signature.convert_data_type(frames)

                    except TypeException as e:
                        msg = "Datatype mismatch of Input parameter. " + str(e)
                        raise TypeException(msg)

            # first argument is self and second is frames.
            output = arg_fn(args[0], frames)

            # check output type
            if output_signature:
                # check shape
                if not (output_signature.check_shape(output)):
                    try:
                        frames = output_signature.reshape(output)
                    except TypeException as e:
                        msg = "Shape mismatch of Output parameter. " + str(e)
                        raise TypeException(msg)

                # check type of output
                if not (output_signature.check_type(output)):
                    try:
                        output = output_signature.convert_data_type(output)

                    except TypeException as e:
                        msg = "Datatype mismatch of Output parameter. " + str(e)
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
