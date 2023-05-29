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
import asyncio

import pandas
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.interfaces.relational.relation import EVARelation
from eva.interfaces.relational.utils import execute_statement, try_binding

from eva.models.server.response import Response
from eva.models.storage.batch import Batch
from eva.parser.alias import Alias
from eva.parser.select_statement import SelectStatement
from eva.parser.utils import (
    parse_create_vector_index,
    parse_load,
    parse_query,
    parse_table_clause,
)
from eva.utils.logging_manager import logger


class EVAConnection:
    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer
        self._cursor = None
        self._result: Batch = None

    def create_vector_index(
        self, index_name: str, table_name: str, expr: str, using: str
    ) -> "EVAConnection":
        """
        Create a vector index on a table in the database.

        Args:
            index_name (str): Name of the index to be created.
            table_name (str): Name of the table on which to build the index.
            expr (str): Expression defining the indexed vector column.
            using (str): Name of the vector indexing method to use.

        Returns:
            EVAConnection: The connection object for executing further operations.
        """
        stmt = parse_create_vector_index(index_name, table_name, expr, using)
        self._result = execute_statement(stmt)
        return self

    def cursor(self) -> "EVACursor":
        """
        Get a cursor for executing database operations.

        Returns:
            EVACursor: The cursor object for executing operations on the database.
        """

        # One unique cursor for one connection
        if self._cursor is None:
            self._cursor = EVACursor(self)
        return self._cursor

    def df(self) -> pandas.DataFrame:
        """
        Get the result of the last executed query on the connection as a pandas
        DataFrame.

        Returns:
            pandas.DataFrame: The result of the query as a DataFrame.

        Raises:
            Exception: If there is no valid result with the current connection.
        """
        if not self._result:
            raise Exception("No valid result with the current connection")
        return self._result.frames

    def load(
        self, file_regex: str, table_name: str, format: str, **kwargs
    ) -> EVARelation:
        """
        Load data from files into a table in the database.

        Args:
            file_regex (str): Regular expression pattern for matching input files.
            table_name (str): Name of the table to be created.
            format (str): File format of the input files.
            **kwargs: Additional keyword arguments for configuring the load operation.

        Returns:
            EVARelation: The EVARelation object representing the loaded table.
        """
        return self.cursor().load(file_regex, table_name, format, **kwargs)

    def sql(self, sql_query: str) -> EVARelation:
        """
        Execute a SQL query.

        Args:
            sql_query (str): The SQL query to execute.

        Returns:
            EVARelation: The EVARelation object representing the result of the query.
        """
        return self.cursor().sql(sql_query)

    def table(self, table_name: str) -> EVARelation:
        """
        Get a EVARelation object representing a table in the database.

        Args:
            table_name (str): Name of the table.

        Returns:
            EVARelation: The EVARelation object representing the table.
        """
        return self.cursor().table(table_name)

    def query(self, sql_query: str) -> EVARelation:
        """
        Execute a SQL query.

        Args:
            sql_query (str): The SQL query to execute.

        Returns:
            EVARelation: The EVARelation object representing the result of the query.
        """
        return self.cursor().query(sql_query)


class EVACursor(object):
    def __init__(self, connection):
        self._connection = connection
        self._pending_query = False
        self._result = None

    async def execute_async(self, query: str):
        """
        Send query to the EVA server.
        """
        if self._pending_query:
            raise SystemError(
                "EVA does not support concurrent queries. \
                    Call fetch_all() to complete the pending query"
            )
        query = self._multiline_query_transformation(query)
        self._connection._writer.write((query + "\n").encode())
        await self._connection._writer.drain()
        self._pending_query = True
        return self

    async def fetch_one_async(self) -> Response:
        """
        fetch_one returns one batch instead of one row for now.
        """
        response = Response()
        prefix = await self._connection._reader.readline()
        if prefix != b"":
            message_length = int(prefix)
            message = await self._connection._reader.readexactly(message_length)
            response = Response.deserialize(message)
        self._pending_query = False
        return response

    async def fetch_all_async(self) -> Response:
        """
        fetch_all is the same as fetch_one for now.
        """
        return await self.fetch_one_async()

    def _multiline_query_transformation(self, query: str) -> str:
        query = query.replace("\n", " ")
        query = query.lstrip()
        query = query.rstrip(" ;")
        query += ";"
        logger.debug("Query: " + query)
        return query

    def stop_query(self):
        self._pending_query = False

    def __getattr__(self, name):
        """
        Auto generate sync function calls from async
        Sync function calls should not be used in an async environment.
        """
        try:
            func = object.__getattribute__(self, "%s_async" % name)
        except Exception as e:
            raise e

        def func_sync(*args, **kwargs):
            loop = asyncio.get_event_loop()
            res = loop.run_until_complete(func(*args, **kwargs))
            return res

        return func_sync

    def table(self, table_name: str) -> EVARelation:
        """
        Get a EVARelation object representing a table in the database.

        Args:
            table_name (str): Name of the table.

        Returns:
            EVARelation: The EVARelation object representing the table.
        """
        table = parse_table_clause(table_name)
        # SELECT * FROM table
        select_stmt = SelectStatement(
            target_list=[TupleValueExpression(col_name="*")], from_table=table
        )
        try_binding(select_stmt)
        return EVARelation(select_stmt, alias=Alias(table_name.lower()))

    def df(self) -> pandas.DataFrame:
        """
        Get the result of the last executed query on the cursor as a pandas
        DataFrame.

        Returns:
            pandas.DataFrame: The result of the query as a DataFrame.

        Raises:
            Exception: If there is no valid result with the current cursor.
        """
        if not self._result:
            raise Exception("No valid result with the current connection")
        return self._result.frames

    def create_vector_index(
        self, index_name: str, table_name: str, expr: str, using: str
    ) -> "EVACursor":
        """
        Create a vector index on a table in the database.

        Args:
            index_name (str): Name of the index to be created.
            table_name (str): Name of the table on which to build the index.
            expr (str): Expression defining the indexed vector column.
            using (str): Name of the vector indexing method to use.

        Returns:
            EVACursor: The cursor object for executing further operations.
        """
        stmt = parse_create_vector_index(index_name, table_name, expr, using)
        self._result = execute_statement(stmt)
        return self

    def load(
        self, file_regex: str, table_name: str, format: str, **kwargs
    ) -> EVARelation:
        """
        Load data from files into a table in the database.

        Args:
            file_regex (str): Regular expression pattern for matching input files.
            table_name (str): Name of the table to be created.
            format (str): File format of the input files.
            **kwargs: Additional keyword arguments for configuring the load operation.

        Returns:
            EVARelation: The EVARelation object representing the loaded table.
        """
        # LOAD {FORMAT} file_regex INTO table_name
        stmt = parse_load(table_name, file_regex, format, **kwargs)
        return EVARelation(stmt)

    def query(self, sql_query: str) -> EVARelation:
        """
        Execute a SQL query.

        Args:
            sql_query (str): The SQL query to execute.

        Returns:
            EVARelation: The EVARelation object representing the result of the query.
        """
        stmt = parse_query(sql_query)
        return EVARelation(stmt)

    def sql(self, sql_query: str) -> EVARelation:
        """
        Execute a SQL query.

        Args:
            sql_query (str): The SQL query to execute.

        Returns:
            EVARelation: The EVARelation object representing the result of the query.
        """
        return self.query(sql_query)


async def get_connection(host: str, port: int) -> EVAConnection:
    reader, writer = await asyncio.open_connection(host, port)
    connection = EVAConnection(reader, writer)
    return connection


def connect(host: str = "0.0.0.0", port: int = 8803) -> EVAConnection:
    """
    Connect to the EVA server and return a connection object.

    Args:
        host (str): The hostname or IP address of the EVA server. Default is "0.0.0.0".
        port (int): The port number of the EVA server. Default is 8803.

    Returns:
        EVAConnection: A connection object representing the connection to the EVA server.
    """
    connection = asyncio.run(get_connection(host, port))
    return connection
