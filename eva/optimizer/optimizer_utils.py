# coding=utf-8
# Copyright 2018-2020 EVA
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

from eva.catalog.catalog_manager import CatalogManager
from eva.parser.create_statement import ColumnDefinition
from eva.utils.logging_manager import LoggingLevel
from eva.utils.logging_manager import LoggingManager


def column_definition_to_udf_io(
        col_list: List[ColumnDefinition], is_input: bool):
    """Create the UdfIO object fro each column definition provided

    Arguments:
        col_list(List[ColumnDefinition]): parsed input/output definitions
        is_input(bool): true if input else false
    """
    if isinstance(col_list, ColumnDefinition):
        col_list = [col_list]

    result_list = []
    for col in col_list:
        if col is None:
            LoggingManager().log(
                "Empty column definition while creating udf io",
                LoggingLevel.ERROR)
            result_list.append(col)
        result_list.append(
            CatalogManager().udf_io(col.name, col.type,
                                    array_type=col.array_type,
                                    dimensions=col.dimension,
                                    is_input=is_input)
        )
    return result_list
