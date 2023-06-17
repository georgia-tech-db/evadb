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
from typing import List, Type

from evadb.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from evadb.udfs.abstract.abstract_udf import AbstractUDF


def load_io_from_udf_decorators(
    udf: Type[AbstractUDF], is_input=False
) -> List[Type[UdfIOCatalogEntry]]:
    """Load the inputs/outputs from the udf decorators and return a list of UdfIOCatalogEntry objects

    Args:
        udf (Object): UDF object
        is_input (bool, optional): True if inputs are to be loaded. Defaults to False.

    Returns:
        Type[UdfIOCatalogEntry]: UdfIOCatalogEntry object created from the input decorator in setup
    """
    tag_key = "input" if is_input else "output"
    io_signature = None
    if hasattr(udf.forward, "tags") and tag_key in udf.forward.tags:
        io_signature = udf.forward.tags[tag_key]
    else:
        # Attempt to populate from the parent class and stop at the first parent class
        # where the required tags are found.
        for base_class in udf.__bases__:
            if hasattr(base_class, "forward") and hasattr(base_class.forward, "tags"):
                if tag_key in base_class.forward.tags:
                    io_signature = base_class.forward.tags[tag_key]
                    break

    assert (
        io_signature is not None
    ), f"Cannot infer io signature from the decorator for {udf}."

    result_list = []
    for io in io_signature:
        result_list.extend(io.generate_catalog_entries(is_input))
    return result_list
