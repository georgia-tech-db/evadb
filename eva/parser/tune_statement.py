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

from eva.expression.abstract_expression import AbstractExpression
from eva.parser.statement import AbstractStatement
from eva.parser.types import StatementType
from eva.parser.table_ref import TableInfo

class TuneStatement(AbstractStatement):
    """
    Tune Statement constructed after parsing the input query

    Arguments:
    table: table to load from
    batch: batch size
    epochs: number of epochs
    freeze_layer: number of freeze layer
    multi_scale: whether to enable multi_scale
    show_train_progress: whether to show whole train progress
    """

    def __init__(
        self,
        table_info: TableInfo,
        batch_size: int,
        epochs_size: int,
        freeze_layer: int,
        multi_scale: bool,
        show_train_progress: bool,
    ):
        super().__init__(StatementType.TUNE)
        self._table_info = table_info,
        self._batch_size = batch_size
        self._epochs_size = epochs_size
        self._freeze_layer = freeze_layer
        self._multi_scale = multi_scale
        self._show_train_progress = show_train_progress

    @property
    def table_info(self) -> TableInfo:
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

    def __str__(self) -> str:
        return "TUNE {} BATCH {} EPOCHS {} FREEZE {} MULTI {} SHOW {}".format(self._table_info, self._batch_size, 
                                                                              self._epochs_size, self._freeze_layer,
                                                                              self._multi_scale, self._show_train_progress)


    def __eq__(self, other):
        if not isinstance(other, TuneStatement):
            return False
        return (
            self.table_info == other.table_info
            and self.batch_size == other.batch_size
            and self.epochs_size == other.epochs_size
            and self.freeze_layer == other.freeze_layer
            and self.multi_scale == other.multi_scale
            and self.show_train_progress == other.show_train_progress
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