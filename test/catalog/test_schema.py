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
import unittest

from src.catalog.schema import ColumnType
from src.catalog.schema import Column
from src.catalog.schema import Schema


class SchemaTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_schema(self):

        schema_name = "foo"
        column_1 = Column("frame_id", ColumnType.INTEGER, False)
        column_2 = Column("frame_data", ColumnType.NDARRAY, False, [28, 28])
        column_3 = Column("frame_label", ColumnType.INTEGER, False)

        schema = Schema(schema_name,
                        [column_1, column_2, column_3])
        print(schema)


if __name__ == '__main__':

    unittest.main()
