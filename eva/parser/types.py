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
from enum import Enum, auto, unique


class ColumnConstraintEnum(Enum):
    NOTNULL = auto()
    DEFAULT = auto()
    PRIMARY = auto()
    UNIQUE = auto()


@unique
class StatementType(Enum):
    """
    Manages enums for all the sql-like statements supported
    """

    SELECT = (auto(),)
    CREATE = (auto(),)
    RENAME = (auto(),)
    DROP = (auto(),)
    INSERT = (auto(),)
    CREATE_UDF = (auto(),)
    LOAD_DATA = (auto(),)
    UPLOAD = (auto(),)
    CREATE_MATERIALIZED_VIEW = (auto(),)
    SHOW = (auto(),)
    DROP_UDF = auto()
    EXPLAIN = (auto(),)
    # add other types


@unique
class ParserOrderBySortType(Enum):
    """
    Manages enums for all order by sort types
    """

    ASC = auto()
    DESC = auto()


@unique
class JoinType(Enum):
    LATERAL_JOIN = auto()
    INNER_JOIN = auto()


@unique
class FileFormatType(Enum):
    """
    Manages enums for all order by sort types
    """

    VIDEO = auto()
    CSV = auto()


@unique
class ShowType(Enum):
    UDFS = auto()
    TABLES = auto()
