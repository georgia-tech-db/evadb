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
from lark.tree import Tree

# from eva.expression.constant_value_expression import ConstantValueExpression
from eva.parser.tune_statement import TuneStatement

##################################################################
# TUNE STATEMENT
##################################################################
class Tune:
    def tune_statement(self, tree):
        file_name = tree.children[1].children[0].children[0].value
        batch_size = tree.children[3].children[0].children[0].value
        epochs_size = tree.children[5].children[0].children[0].value
        freeze_layer = tree.children[7].children[0].children[0].value
        learning_rate = tree.children[9].children[0].children[0].value
        show_train_progress = tree.children[11].children[0].children[0].value
        stmt = TuneStatement(file_name, batch_size, epochs_size, freeze_layer, learning_rate, show_train_progress)
        return stmt

    def file_name(self, tree):
        file_name = tree.children[1].children[0].children[0].value
        return file_name

    def batch_size(self, tree):
        batch_size = tree.children[3].children[0].children[0].value
        return batch_size

    def epochs_size(self, tree):
        epochs_size = tree.children[5].children[0].children[0].value
        return epochs_size
    
    def freeze_layer(self, tree):
        freeze_layer = tree.children[7].children[0].children[0].value
        return freeze_layer
    
    def learning_rate(self, tree):
        learning_rate = tree.children[9].children[0].children[0].value
        return learning_rate
    
    def show_train_progress(self, tree):
        show_train_progress = tree.children[11].children[0].children[0].value
        return show_train_progress