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

from eva.utils.generic_utils import EVAEnum


class ColumnConstraintEnum(EVAEnum):
    NOTNULL  # noqa: F821
    DEFAULT  # noqa: F821
    PRIMARY  # noqa: F821
    UNIQUE  # noqa: F821


class StatementType(EVAEnum):
    """
    Manages EVAEnums for all the sql-like statements supported
    """

    SELECT  # noqa: F821
    CREATE  # noqa: F821
    RENAME  # noqa: F821
    DROP  # noqa: F821
    INSERT  # noqa: F821
    CREATE_UDF  # noqa: F821
    LOAD_DATA  # noqa: F821
    UPLOAD  # noqa: F821
    CREATE_MATERIALIZED_VIEW  # noqa: F821
    SHOW  # noqa: F821
    DROP_UDF  # noqa: F821
    EXPLAIN  # noqa: F821
    CREATE_INDEX  # noqa: F821
    # add other types


class ParserOrderBySortType(EVAEnum):
    """
    Manages EVAEnums for all order by sort types
    """

    ASC  # noqa: F821
    DESC  # noqa: F821


class JoinType(EVAEnum):
    LATERAL_JOIN  # noqa: F821
    INNER_JOIN  # noqa: F821


class FileFormatType(EVAEnum):
    VIDEO  # noqa: F821
    CSV  # noqa: F821
    IMAGE  # noqa: F821


class ShowType(EVAEnum):
    UDFS  # noqa: F821
    TABLES  # noqa: F821
