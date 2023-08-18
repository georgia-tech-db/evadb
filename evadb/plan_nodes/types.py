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
from enum import Enum, auto, unique


# Modified, add RENAME
@unique
class PlanOprType(Enum):
    SEQUENTIAL_SCAN = auto()
    STORAGE_PLAN = auto()
    PP_FILTER = auto()
    INSERT = auto()
    DELETE = auto()
    CREATE = auto()
    RENAME = auto()
    DROP_OBJECT = auto()
    CREATE_UDF = auto()
    LOAD_DATA = auto()
    UNION = auto()
    GROUP_BY = auto()
    ORDER_BY = auto()
    LIMIT = auto()
    SAMPLE = auto()
    FUNCTION_SCAN = auto()
    NESTED_LOOP_JOIN = auto()
    HASH_JOIN = auto()
    LATERAL_JOIN = auto()
    HASH_BUILD = auto()
    EXCHANGE = auto()
    PREDICATE_FILTER = auto()
    PROJECT = auto()
    SHOW_INFO = auto()
    EXPLAIN = auto()
    CREATE_INDEX = auto()
    APPLY_AND_MERGE = auto()
    VECTOR_INDEX_SCAN = auto()
    NATIVE = auto()
    SQLALCHEMY = auto()
    # add other types
