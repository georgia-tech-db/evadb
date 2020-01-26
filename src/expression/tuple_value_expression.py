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
from .abstract_expression import AbstractExpression, ExpressionType, \
    ExpressionReturnType


class TupleValueExpression(AbstractExpression):
    def __init__(self, col_idx: int = None, col_name: str = None):
        # setting return type to be invalid not sure if that is correct
        # no child so that is okay
        super().__init__(ExpressionType.TUPLE_VALUE,
                         rtype=ExpressionReturnType.INVALID)
        self._col_name = col_name
        # todo
        self._table_name = None
        self._col_idx = col_idx

    # def evaluate(AbstractTuple tuple1, AbstractTuple tuple2):

    # don't know why are we getting 2 tuples
    # comments added to abstract class,
    # maybe we should move to *args

    # assuming tuple1 to be valid

    # remove this once doen with tuple class
    def evaluate(self, *args):
        tuple1 = None
        if args is None:
            # error Handling
            pass
        tuple1 = args[0]
        return tuple1[(self._col_idx)]

    # ToDo
    # implement other boilerplate functionality
