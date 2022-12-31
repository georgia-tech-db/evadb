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
from lark import Tree

from eva.parser.types import FileFormatType
from eva.parser.upload_statement import UploadStatement


class Upload:
    def upload_statement(self, tree):
        srv_path = None
        video_blob = None
        table_info = None
        column_list = None

        # default file format
        file_format = FileFormatType.VIDEO
        file_options = {}
        file_options["file_format"] = file_format

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "file_name":
                    srv_path = self.visit(child).value
                elif child.data == "video_blob":
                    video_blob = self.visit(child).value
                elif child.data == "table_name":
                    table_info = self.visit(child)
                elif child.data == "uid_list":
                    column_list = self.visit(child)
                elif child.data == "file_options":
                    file_options = self.visit(child)

        stmt = UploadStatement(
            srv_path, video_blob, table_info, column_list, file_options
        )
        return stmt
