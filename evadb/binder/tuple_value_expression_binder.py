# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from evadb.binder.statement_binder import StatementBinder
from evadb.catalog.catalog_type import VideoColumnName
from evadb.expression.tuple_value_expression import TupleValueExpression


def bind_tuple_expr(binder: StatementBinder, node: TupleValueExpression):
    table_alias, col_obj = binder._binder_context.get_binded_column(
        node.name, node.table_alias
    )
    node.table_alias = table_alias
    if node.name == VideoColumnName.audio:
        binder._binder_context.enable_audio_retrieval()
    if node.name == VideoColumnName.data:
        binder._binder_context.enable_video_retrieval()
    node.col_alias = "{}.{}".format(table_alias, node.name.lower())
    node.col_object = col_obj
