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

from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
from eva.parser.types import StatementType


class SelectLikeStatement(AbstractStatement):
    """Select Like Statement constructed after parsing the input query

    Attributes:
        table_ref: TableRef
            target table.
        target_img: str
            target image file path.
    """

    def __init__(
        self,
        table_ref: TableRef,
        target_img: str,
    ):
        super().__init__(StatementType.SELECT_LIKE)
        self._table_ref = table_ref
        self._target_img = target_img

    def __str__(self) -> str:
        print_str = "SELECT FROM {} LIKE {}".format(
            self._table_ref,
            self._target_img
        )
        return print_str

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def target_img(self):
        return self._target_img

    def __eq__(self, other):
        if not isinstance(other, SelectLikeStatement):
            return False
        return (
            self._table_ref == other._table_ref
            and self._target_img == other._target_img
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self._table_ref,
                self._target_img
            )
        )
