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
from enum import IntEnum, unique


class ColumnConstraintEnum(IntEnum):
    NULLNOTNULL = 1
    DEFAULT = 2
    PRIMARY = 3
    UNIQUE = 4


# Modified, add RENAME, add TRUNCATE
@unique
class StatementType(IntEnum):
    """
    Manages enums for all the sql-like statements supported
    """
    SELECT = 1,
    CREATE = 2,
    INSERT = 3,
    CREATE_UDF = 4,
    LOAD_DATA = 5,
    UPLOAD = 6,
    RENAME = 7,
    TRUNCATE = 8,
    DROP = 9,
    # add other types


@unique
class ParserOrderBySortType(IntEnum):
    """
    Manages enums for all order by sort types
    """
    ASC = 1
    DESC = 2
