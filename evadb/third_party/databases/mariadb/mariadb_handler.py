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
import mariadb
import pandas as pd

from evadb.third_party.databases.types import (
    DBHandler,
    DBHandlerResponse,
    DBHandlerStatus,
)


class MariaDbHandler(DBHandler):

    """
    Class for implementing the Maria DB handler as a backend store for
    EvaDB.
    """

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

    def connect(self):
        """
        Establish connection to the database.
        Returns:
          DBHandlerStatus
        """
        try:
            self.connection = mariadb.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            # Auto commit is off by default.
            self.connection.autocommit = True
            return DBHandlerStatus(status=True)
        except mariadb.Error as e:
            return DBHandlerStatus(status=False, error=str(e))

    def disconnect(self):
        """
        Disconnect from the database.
        """
        if self.connection:
            self.connection.close()

    def get_sqlalchmey_uri(self) -> str:
        return f"mariadb+mariadbconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def check_connection(self) -> DBHandlerStatus:
        """
        Method for checking the status of database connection.
        Returns:
          DBHandlerStatus
        """
        if self.connection:
            return DBHandlerStatus(status=True)
        else:
            return DBHandlerStatus(status=False, error="Not connected to the database.")

    def get_tables(self) -> DBHandlerResponse:
        """
        Method to get the list of tables from database.
        Returns:
          DBHandlerStatus
        """
        if not self.connection:
            return DBHandlerResponse(data=None, error="Not connected to the database.")

        try:
            query = f"SELECT table_name as 'table_name' FROM information_schema.tables WHERE table_schema='{self.database}'"
            tables_df = pd.read_sql_query(query, self.connection)
            return DBHandlerResponse(data=tables_df)
        except mariadb.Error as e:
            return DBHandlerResponse(data=None, error=str(e))

    def get_columns(self, table_name: str) -> DBHandlerResponse:
        """
        Method to retrieve the columns of the specified table from the database.
        Args:
          table_name (str): name of the table whose columns are to be retrieved.
        Returns:
          DBHandlerStatus
        """
        if not self.connection:
            return DBHandlerResponse(data=None, error="Not connected to the database.")

        try:
            query = f"SELECT column_name as 'name', data_type as 'dtype' FROM information_schema.columns WHERE table_name='{table_name}'"
            columns_df = pd.read_sql_query(query, self.connection)
            columns_df["dtype"] = columns_df["dtype"].apply(
                self._mariadb_to_python_types
            )
            return DBHandlerResponse(data=columns_df)
        except mariadb.Error as e:
            return DBHandlerResponse(data=None, error=str(e))

    def _fetch_results_as_df(self, cursor):
        """
        Fetch results from the cursor for the executed query and return the
        query results as dataframe.
        """
        try:
            res = cursor.fetchall()
            res_df = pd.DataFrame(
                res, columns=[desc[0].lower() for desc in cursor.description]
            )
            return res_df
        except mariadb.ProgrammingError as e:
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
        except mariadb.Error as e:
            return DBHandlerResponse(data=None, error=str(e))

    def _mariadb_to_python_types(self, mariadb_type: str):
        mapping = {
            "tinyint": int,
            "smallint": int,
            "mediumint": int,
            "bigint": int,
            "int": int,
            "decimal": float,
            "float": float,
            "double": float,
            "text": str,
            "string literals": str,
            "char": str,
            "varchar": str,
            "boolean": bool,
            # Add more mappings as needed
        }

        if mariadb_type in mapping:
            return mapping[mariadb_type]
        else:
            raise Exception(
                f"Unsupported column {mariadb_type} encountered in the MariaDB. Please raise a feature request!"
            )
