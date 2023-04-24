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

from eva.expression.constant_value_expression import ConstantValueExpression
from eva.parser.table_ref import TableInfo
from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.plan_nodes.types import PlanOprType


class TunePlan(AbstractPlan):
    """
    This plan is used for storing information required for tune
    operations.

    Arguments:
        table: table to load from
        batch: batch size
        epochs: number of epochs
        freeze_layer: number of freeze_layer
        multi-scale: whether to enable multi-scale
        show_train_progress: whether to show whole train progress
    """

    def __init__(
        self,
        table_info: TableInfo,
        batch_size: ConstantValueExpression,
        epochs_size: ConstantValueExpression,
        freeze_layer: ConstantValueExpression,
        multi_scale: bool,
        show_train_progress: bool,
    ):
        self._table_info = table_info
        self._batch_size = batch_size
        self._epochs_size = epochs_size
        self._freeze_layer = freeze_layer
        self._multi_scale = multi_scale
        self._show_train_progress = show_train_progress
        super().__init__(PlanOprType.TUNE)

    @property
    def table_info(self):
        return self._table_info

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
    def multi_scale(self):
        return self._multi_scale

    @property
    def show_train_progress(self):
        return self._show_train_progress

    def __str__(self):
        return "TunePlan(table={}, batch_size={}, epochs_size={}, freeze_layer={}, multi_scale={}, show_train_progress={})".format(
            self.table_info,
            self.batch_size,
            self.epochs_size,
            self.freeze_layer,
            self.multi_scale,
            self.show_train_progress,
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_info,
                self.batch_size,
                self.epochs_size,
                self.freeze_layer,
                self.multi_scale,
                self.show_train_progress,
            )
        )
