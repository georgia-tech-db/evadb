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
from eva.parser.evaql.evaql_parser import evaql_parser
from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from eva.parser.table_ref import TableRef
from eva.parser.types import FileFormatType
from eva.parser.upload_statement import UploadStatement


class Upload(evaql_parserVisitor):
    def visitUploadStatement(self, ctx: evaql_parser.UploadStatementContext):
        srv_path = self.visit(ctx.fileName()).value
        video_blob = self.visit(ctx.videoBlob()).value
        table = TableRef(self.visit(ctx.tableName()))

        # Set default for file_format as Video
        file_format = FileFormatType.VIDEO
        file_options = {}
        file_options["file_format"] = file_format

        if ctx.fileOptions():
            file_options = self.visit(ctx.fileOptions())

        # set default for column_list as None
        column_list = None
        if ctx.uidList():
            column_list = self.visit(ctx.uidList())

        stmt = UploadStatement(srv_path, video_blob, table, column_list, file_options)
        return stmt
