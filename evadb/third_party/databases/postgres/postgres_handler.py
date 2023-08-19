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
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")
        self.user = kwargs.get("user")
        self.password = kwargs.get("password")
        self.database = kwargs.get("database")

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            self.connection.autocommit = True
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

    def _fetch_results_as_df(self, cursor):
        """
        This is currently the only clean solution that we have found so far.
        Reference to Postgres API: https://www.psycopg.org/docs/cursor.html#fetch

        In short, currently there is no very clean programming way to differentiate
        CREATE, INSERT, SELECT. CREATE and INSERT do not return any result, so calling
        fetchall() on those will yield a programming error. Cursor has an attribute
        rowcount, but it indicates # of rows that are affected. In that case, for both
        INSERT and SELECT rowcount is not 0, so we also cannot use this API to
        differentiate INSERT and SELECT.
        """
        try:
            res = cursor.fetchall()
            res_df = pd.DataFrame(res, columns=[desc[0] for desc in cursor.description])
            return res_df
        except psycopg2.ProgrammingError as e:
            if str(e) == "no results to fetch":
                return pd.DataFrame({"status": ["success"]})
            raise e

    def execute_native_query(self, query_string: str) -> DBHandlerResponse:
        if not self.connection:
            return DBHandlerResponse(data=None, error="Not connected to the database.")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            return DBHandlerResponse(data=self._fetch_results_as_df(cursor))
        except psycopg2.Error as e:
            return DBHandlerResponse(data=None, error=str(e))
