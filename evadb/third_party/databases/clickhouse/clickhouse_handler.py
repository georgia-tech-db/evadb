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
from sqlalchemy import create_engine

from evadb.third_party.databases.types import (
    DBHandler,
    DBHandlerResponse,
    DBHandlerStatus,
)


class ClickHouseHandler(DBHandler):
    def __init__(self, name: str, **kwargs):
        """
        Initialize the handler.
        Args:
            name (str): name of the DB handler instance
            **kwargs: arbitrary keyword arguments for establishing the connection.
        """
        super().__init__(name)
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")
        self.user = kwargs.get("user")
        self.password = kwargs.get("password")
        self.database = kwargs.get("database")
        self.protocol = kwargs.get("protocol")
        protocols_map = {
            "native": "clickhouse+native",
            "http": "clickhouse+http",
            "https": "clickhouse+https",
        }
        if self.protocol in protocols_map:
            self.protocol = protocols_map[self.protocol]

    def connect(self):
        """
        Set up the connection required by the handler.
        Returns:
            DBHandlerStatus
        """
        try:
            protocol = self.protocol
            host = self.host
            port = self.port
            user = self.user
            password = self.password
            database = self.database
            url = f"{protocol}://{user}:{password}@{host}:{port}/{database}"
            if self.protocol == "clickhouse+https":
                url = url + "?protocol=https"

            engine = create_engine(url)
            self.connection = engine.raw_connection()
            return DBHandlerStatus(status=True)
        except Exception as e:
            return DBHandlerStatus(status=False, error=str(e))

    def disconnect(self):
        """
        Close any existing connections.
        """
        if self.connection:
            self.disconnect()

    def check_connection(self) -> DBHandlerStatus:
        """
        Check connection to the handler.
        Returns:
            DBHandlerStatus
        """
        if self.connection:
            return DBHandlerStatus(status=True)
        else:
            return DBHandlerStatus(status=False, error="Not connected to the database.")

    def get_tables(self) -> DBHandlerResponse:
        """
        Return the list of tables in the database.
        Returns:
            DBHandlerResponse
        """
        if not self.connection:
            return DBHandlerResponse(data=None, error="Not connected to the database.")

        try:
            query = f"SHOW TABLES FROM {self.connection_data['database']}"
            tables_df = pd.read_sql_query(query, self.connection)
            return DBHandlerResponse(data=tables_df)
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))

    def get_columns(self, table_name: str) -> DBHandlerResponse:
        """
        Returns the list of columns for the given table.
        Args:
            table_name (str): name of the table whose columns are to be retrieved.
        Returns:
            DBHandlerResponse
        """
        if not self.connection:
            return DBHandlerResponse(data=None, error="Not connected to the database.")

        try:
            query = f"DESCRIBE {table_name}"
            columns_df = pd.read_sql_query(query, self.connection)
            columns_df["dtype"] = columns_df["dtype"].apply(
                self._clickhouse_to_python_types
            )
            return DBHandlerResponse(data=columns_df)
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))

    def _fetch_results_as_df(self, cursor):
        try:
            res = cursor.fetchall()
            if not res:
                return pd.DataFrame({"status": ["success"]})
            res_df = pd.DataFrame(res, columns=[desc[0] for desc in cursor.description])
            return res_df
        except Exception as e:
            if str(e) == "no results to fetch":
                return pd.DataFrame({"status": ["success"]})
            raise e

    def execute_native_query(self, query_string: str) -> DBHandlerResponse:
        """
        Executes the native query on the database.
        Args:
            query_string (str): query in native format
        Returns:
            DBHandlerResponse
        """
        if not self.connection:
            return DBHandlerResponse(data=None, error="Not connected to the database.")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            return DBHandlerResponse(data=self._fetch_results_as_df(cursor))
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))

    def _clickhouse_to_python_types(self, clickhouse_type: str):
        mapping = {
            "char": str,
            "varchar": str,
            "text": str,
            "boolean": bool,
            "integer": int,
            "int": int,
            "float": float,
            "double": float,
            # Add more mappings as needed
        }

        if clickhouse_type in mapping:
            return mapping[clickhouse_type]
        else:
            raise Exception(
                f"Unsupported column {clickhouse_type} encountered in the clickhouse table. Please raise a feature request!"
            )
