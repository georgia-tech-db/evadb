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
from eva.parser.table_ref import TableRef
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class SelectLikePlan(AbstractPlan):
    """
    This plan is used for similarity search on a target image from a table

    Attributes:
        table_ref: TableRef
            target table
        target_img: str
            target image file path.
    """

    def __init__(
        self,
        table_ref: TableRef,
        target_img: str
    ):
        super().__init__(PlanOprType.SELECT_LIKE)
        self._table_ref = table_ref
        self._target_img = target_img

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def target_img(self):
        return self._target_img

    def __eq__(self, other):
        if not isinstance(other, SelectLikePlan):
            return False
        return (
            self._table_ref == other._table_ref
            and self._target_img== other._target_img
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self._table_ref,
                self._target_img
            )
        )
