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
import unittest
from test.util import get_all_subclasses

from sqlalchemy import inspect

from eva.catalog.services.base_service import BaseService
from eva.catalog.sql_config import SQLConfig


class SQLAlchemyTests(unittest.TestCase):
    def test_sqlalchemy_verify_catalog_tables(self):
        sql_session = SQLConfig().session
        engine = sql_session.get_bind()
        insp = inspect(engine)
        table_names = insp.get_table_names()

        try:
            for table in table_names:
                column_infos = insp.get_columns(table)
                # Skip video tables
                if len(column_infos) <= 2:
                    continue
                print("\n" + table, end=" : ")
                self.assertTrue(len(column_infos) < 10, f"{table} has too many columns")
                for column_info in column_infos:
                    print(column_info["name"], end=" | ")

            service_subclasses = get_all_subclasses(BaseService)
            for service_subclass in service_subclasses:
                service = service_subclass()
                table_tuples = service.get_all_entries()
                self.assertTrue(
                    len(table_tuples) < 100
                ), f"{service_subclass} table has too many tuples"
        finally:
            sql_session.close()
