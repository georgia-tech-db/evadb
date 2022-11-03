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
from typing import List

from eva.catalog.models.df_column import DataFrameColumn
from eva.parser.types import JoinType
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class HashJoinBuildPlan(AbstractPlan):
    """
    This plan is used for storing information required for hashjoin build side.
    It prepares the hash table of preferably the smaller relation
    which is used by the probe side to find relevant rows.
    Arguments:
        build_keys (List[DataFrameColumn]) : list of equi-key columns.
                        If empty, then Cartitian product.
    """

    def __init__(self, join_type: JoinType, build_keys: List[DataFrameColumn]):
        self.join_type = join_type
        self.build_keys = build_keys
        super().__init__(PlanOprType.HASH_BUILD)

    def __str__(self):
        return "HashJoinBuildPlan(join_type={}, \
            build_keys={})".format(
            self.join_type, self.build_keys
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.join_type, tuple(self.build_keys or [])))
