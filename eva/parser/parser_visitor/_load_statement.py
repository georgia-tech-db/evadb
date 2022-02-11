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

from eva.parser.load_statement import LoadDataStatement
from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from eva.parser.evaql.evaql_parser import evaql_parser

from eva.parser.table_ref import TableRef
from eva.parser.types import FileFormatType


class Load(evaql_parserVisitor):
    def visitLoadStatement(self, ctx: evaql_parser.LoadStatementContext):
        file_path = self.visit(ctx.fileName()).value
        table = TableRef(self.visit(ctx.tableName()))

        # Set defualt as Video
        file_format = FileFormatType.VIDEO
        other_options = None
        if ctx.fileOptions():
            file_format, other_options = self.visit(ctx.fileOptions())
        stmt = LoadDataStatement(table, file_path, file_format, other_options)
        return stmt

    def visitFileOptions(self, ctx: evaql_parser.FileOptionsContext):
        file_format = FileFormatType.VIDEO
        # Check the file format 
        if ctx.CSV() is not None:
            file_format = FileFormatType.CSV

        # parse and add more file options in future
        other_options = None
        return file_format, other_options
