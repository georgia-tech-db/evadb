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
import pandas as pd
import psycopg2

from evadb.third_party.databases.types import (
    DBHandler,
    DBHandlerResponse,
    DBHandlerStatus,
)


class PostgresHandler(DBHandler):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.params = kwargs.get("params", None)

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.params.get("host"),
                port=self.params.get("port"),
                user=self.params.get("username"),
                password=self.params.get("password"),
                database=self.params.get("database"),
            )
            return DBHandlerStatus(status=True)
        except psycopg2.Error as e:
            return DBHandlerStatus(status=False, error=str(e))

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def check_connection(self) -> DBHandlerStatus:
        if self.connection:
            return DBHandlerStatus(status=True)
        else:
            return DBHandlerStatus(status=False, error="Not connected to the database.")

    def get_tables(self) -> DBHandlerResponse:
        if not self.connection:
            return DBHandlerResponse(data=None, error="Not connected to the database.")

        try:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog')"
            tables_df = pd.read_sql_query(query, self.connection)
            return DBHandlerResponse(data=tables_df)
        except psycopg2.Error as e:
            return DBHandlerResponse(data=None, error=str(e))

    def get_columns(self, table_name: str) -> DBHandlerResponse:
        if not self.connection:
            return DBHandlerResponse(data=None, error="Not connected to the database.")

        try:
            query = f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'"
            columns_df = pd.read_sql_query(query, self.connection)
            return DBHandlerResponse(data=columns_df)
        except psycopg2.Error as e:
            return DBHandlerResponse(data=None, error=str(e))
