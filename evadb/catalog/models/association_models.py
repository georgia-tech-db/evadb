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
from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint

from evadb.catalog.models.base_model import BaseModel

# dependency table to maintain a many-to-many relationship between function_catalog and function_cache_catalog. This is important to ensure that any changes to function are propagated to function_cache. For example, deletion of a function should also clear the associated caches.

depend_function_and_function_cache = Table(
    "depend_function_and_function_cache",
    BaseModel.metadata,
    Column("_function_id", ForeignKey("function_catalog._row_id")),
    Column("_function_cache_id", ForeignKey("function_cache._row_id")),
    UniqueConstraint("_function_id", "_function_cache_id"),
)


depend_column_and_function_cache = Table(
    "depend_column_and_function_cache",
    BaseModel.metadata,
    Column("_col_id", ForeignKey("column_catalog._row_id")),
    Column("_function_cache_id", ForeignKey("function_cache._row_id")),
    UniqueConstraint("_col_id", "_function_cache_id"),
)
