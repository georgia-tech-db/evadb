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


from typing import List

from evadb.udfs.decorators.io_descriptors.abstract_types import IOArgument


def setup(cacheable: bool = False, udf_type: str = "Abstract", batchable: bool = True):
    """decorator for the setup function. It will be used to set the cache, batching and
    udf_type parameters in the catalog

    Args:
        use_cache (bool): True if the udf should be cached
        udf_type (str): Type of the udf
        batch (bool): True if the udf should be batched
    """

    def inner_fn(arg_fn):
        def wrapper(*args, **kwargs):
            # calling the setup function defined by the user inside the udf implementation
            arg_fn(*args, **kwargs)

        tags = {}
        tags["cacheable"] = cacheable
        tags["udf_type"] = udf_type
        tags["batchable"] = batchable
        wrapper.tags = tags
        return wrapper

    return inner_fn


def forward(input_signatures: List[IOArgument], output_signatures: List[IOArgument]):
    """decorator for the forward function. It will be used to set the input and output.

    Args:
        input_signature (List[IOArgument]): List of input arguments for the udf
        output_signature ( List[IOArgument])): List of output arguments for the udf
    """

    def inner_fn(arg_fn):
        def wrapper(*args):
            # calling the forward function defined by the user inside the udf implementation
            return arg_fn(*args)

        tags = {}
        tags["input"] = input_signatures
        tags["output"] = output_signatures
        wrapper.tags = tags
        return wrapper

    return inner_fn
