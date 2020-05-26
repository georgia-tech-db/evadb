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
from enum import Enum, unique
from typing import Callable

from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType
from src.models.storage.batch import Batch


@unique
class ExecutionMode(Enum):
    # EXEC means the executed function mutates the batch frame and returns
    # it back. The frame batch is mutated.
    EXEC = 1
    # EVAL function with return values
    EVAL = 2


class FunctionExpression(AbstractExpression):
    """
    Expression used for function evaluation
    Arguments:
        func (Callable): UDF or EVA built in function for performing
        operations on the

        mode (ExecutionMode): The mode in which execution needs to happen.
        Will just return the output in EVAL mode. EXEC mode updates the
        BatchFrame with output.

        is_temp (bool, default:False): In case of EXEC type, decides if the
        outcome needs to be stored in BatchFrame temporarily.

    """

    def __init__(self, func: Callable,
                 mode: ExecutionMode = ExecutionMode.EVAL, name=None,
                 is_temp: bool = False,
                 **kwargs):
        if mode == ExecutionMode.EXEC:
            assert name is not None

        super().__init__(ExpressionType.FUNCTION_EXPRESSION, **kwargs)
        self.mode = mode
        self.name = name
        self.function = func
        self.is_temp = is_temp

    def evaluate(self, batch: Batch):
        args = []
        if self.get_children_count() > 0:
            child = self.get_child(0)
            args.append(child.evaluate(batch))
        else:
            args.append(batch)

        outcome = self.function(*args)

        if self.mode == ExecutionMode.EXEC:
            batch.set_outcomes(self.name, outcome, is_temp=self.is_temp)
        return outcome
