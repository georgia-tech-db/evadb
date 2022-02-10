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

from eva.planner.types import PlanOprType
from eva.planner.abstract_join_plan import AbstractJoin
from eva.parser.types import JoinType
from eva.catalog.models.df_column import DataFrameColumn


class HashJoinBuildPlan(AbstractJoin):
    """
    This plan is used for storing information required for hashjoin build side.
    It prepares the hash table of preferably the smaller relation
    which is used by the probe side to find relevant rows.
    Arguments:
        join_type: JoinType
        build_keys (List[DataFrameColumn]) : list of equi-key columns.
                        If empty, then Cartitian product.
    """

    def __init__(self,
                 join_type: JoinType,
                 build_keys: List[DataFrameColumn],
                 ):
        super().__init__(PlanOprType.BUILD_JOIN,
                         join_type,
                         build_keys,
                         )
