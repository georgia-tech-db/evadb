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

from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.plan_nodes.types import PlanOprType
from eva.expression.constant_value_expression import ConstantValueExpression

class TunePlan(AbstractPlan):
    """
    This plan is used for storing information required for tune
    operations.

    Arguments:
        batch: batch size
        epochs: number of epochs
    """

    def __init__(
        self,
        file_name: str,
        batch_size: ConstantValueExpression,
        epochs_size: ConstantValueExpression,
        freeze_layer: ConstantValueExpression,
        learning_rate: ConstantValueExpression,
        show_train_progress: bool,
    ):
        self._file_name = file_name
        self._batch_size = batch_size
        self._epochs_size = epochs_size
        self._freeze_layer = freeze_layer
        self._learning_rate = learning_rate
        self._show_train_progress = show_train_progress
        super().__init__(PlanOprType.TUNE)

    @property
    def file_name(self):
        return self._file_name
    
    @property
    def batch_size(self):
        return self._batch_size

    @property
    def epochs_size(self):
        return self._epochs_size
    
    @property
    def freeze_layer(self):
        return self._freeze_layer
    
    @property
    def learning_rate(self):
        return self._learning_rate
    
    @property
    def show_train_progress(self):
        return self._show_train_progress

    def __str__(self):
        return "TunePlan(file_name={}, batch_size={}, epochs_size={}, freeze_layer={}, learning_rate={}, show_train_progress={})".format(
            self.file_name,
            self.batch_size,
            self.epochs_size,
            self.freeze_layer,
            self.learning_rate,
            self.show_train_progress,
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.file_name,
                self.batch_size,
                self.epochs_size,
                self.freeze_layer,
                self.learning_rate,
                self.show_train_progress,
            )
        )