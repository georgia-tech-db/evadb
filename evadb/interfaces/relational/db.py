# coding=utf-8
# Copyright 2018-2023 EVA
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

from eva.configuration.constants import EVA_DATABASE_DIR
from eva.database import EVADatabase, init_eva_db_instance
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.interfaces.relational.relation import EVADBQuery
from eva.interfaces.relational.utils import execute_statement, try_binding
from eva.models.server.response import Response
from eva.models.storage.batch import Batch
from eva.parser.alias import Alias
from eva.parser.select_statement import SelectStatement
from eva.parser.utils import (
    parse_create_udf,
    parse_create_vector_index,
    parse_load,
    parse_query,
    parse_table_clause,
)
from eva.udfs.udf_bootstrap_queries import init_builtin_udfs
from eva.utils.logging_manager import logger


class EVADBConnection:
    def __init__(self, evadb: EVADatabase, reader, writer):
        self._reader = reader
        self._writer = writer
        self._cursor = None
        self._result: Batch = None
        self._evadb = evadb

    def cursor(self):
        """Retrieves a cursor associated with the connection.

        Returns:
            EVADBCursor: The cursor object used to execute queries.


        Examples:
            >>> from eva import connect
            >>> conn = connect()
            >>> cursor = conn.cursor()
        """
        # One unique cursor for one connection
        if self._cursor is None:
            self._cursor = EVADBCursor(self)
        return self._cursor


class EVADBCursor(object):
    def __init__(self, connection):
        self._connection = connection
        self._evadb = connection._evadb
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

    def table(self, table_name: str) -> EVADBQuery:
        """
        Retrieves data from a table in the database.

        Args:
            table_name (str): Name of the table.

        Returns:
            EVADBQuery: The EVADBQuery object representing the table query.
        """
        table = parse_table_clause(table_name)
        # SELECT * FROM table
        select_stmt = SelectStatement(
            target_list=[TupleValueExpression(col_name="*")], from_table=table
        )
        try_binding(self._evadb.catalog, select_stmt)
        return EVADBQuery(self._evadb, select_stmt, alias=Alias(table_name.lower()))

    def df(self) -> pandas.DataFrame:
        """
        Returns the result as a pandas DataFrame.

        Returns:
            pandas.DataFrame: The result as a DataFrame.

        Raises:
            Exception: If no valid result is available with the current connection.
        """
        if not self._result:
            raise Exception("No valid result with the current cursor")
        return self._result.frames

    def create_vector_index(
        self, index_name: str, table_name: str, expr: str, using: str
    ) -> "EVADBCursor":
        """
        Creates a vector index using the provided expr on the table.

        Args:
            index_name (str): Name of the index.
            table_name (str): Name of the table.
            expr (str): Expression used to build the vector index.
            using (str): Method used for indexing, can be `FAISS` or `QDRANT`.

        Returns:
            EVADBCursor: The EVADBCursor object.

        """
        stmt = parse_create_vector_index(index_name, table_name, expr, using)
        self._result = execute_statement(self._evadb, stmt)
        return self

    def load(
        self, file_regex: str, table_name: str, format: str, **kwargs
    ) -> EVADBQuery:
        """
        Loads data from files into a table.

        Args:
            file_regex (str): Regular expression specifying the files to load.
            table_name (str): Name of the table.
            format (str): File format of the data.
            **kwargs: Additional keyword arguments for configuring the load operation.

        Returns:
            EVADBQuery: The EVADBQuery object representing the load query.
        """
        # LOAD {FORMAT} file_regex INTO table_name
        stmt = parse_load(table_name, file_regex, format, **kwargs)
        return EVADBQuery(self._evadb, stmt)

    def create_udf(
        self,
        udf_name: str,
        if_not_exists: bool = True,
        impl_path: str = None,
        type: str = None,
        **kwargs
    ) -> "EVADBQuery":
        """
        Create a udf in the database.

        Args:
            udf_name (str): Name of the udf to be created.
            if_not_exists (bool): If True, do not raise an error if the UDF already exists. If False, raise an error.
            impl_path (str): Path string to udf's implementation.
            type (str): Type of the udf (e.g. HuggingFace).
            **kwargs: Additional keyword arguments for configuring the create udf operation.

        Returns
            EVADBQuery: The EVADBQuery object representing the UDF created.
        """
        stmt = parse_create_udf(udf_name, if_not_exists, impl_path, type, **kwargs)
        return EVADBQuery(self._evadb, stmt)

    def query(self, sql_query: str) -> EVADBQuery:
        """
        Executes a SQL query.

        Args:
            sql_query (str): The SQL query to be executed
        Returns:
            EVADBQuery: The EVADBQuery object.
        """
        stmt = parse_query(sql_query)
        return EVADBQuery(self._evadb, stmt)


def connect(
    eva_dir: str = EVA_DATABASE_DIR, sql_backend: str = None
) -> EVADBConnection:
    """
    Connects to the EVA server and returns a connection object.

    Args:
        eva_dir (str): The directory used by EVA to store database-related content. Default is "eva_db".
        sql_backend (str): Custom database URI to be used. We follow the SQLAlchemy database URL format.
            Default is SQLite in the EVA directory. See https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls.

    Returns:
        EVADBConnection: A connection object representing the connection to the EVA database.
    """

    # As we are not employing a client-server approach for the Pythonic interface, the
    # host and port parameters are irrelevant. Additionally, for the EVADBConnection, the
    # reader and writer parameters are not relevant in the serverless approach.
    evadb = init_eva_db_instance(eva_dir, custom_db_uri=sql_backend)
    init_builtin_udfs(evadb, mode="release")
    return EVADBConnection(evadb, None, None)


# WIP
# support remote connections from pythonic APIs


async def get_connection(host: str, port: int) -> EVADBConnection:
    reader, writer = await asyncio.open_connection(host, port)
    # no db required for remote connection
    connection = EVADBConnection(None, reader, writer)
    return connection


def connect_remote(host: str, port: int) -> EVADBConnection:
    connection = asyncio.run(get_connection(host, port))
    return connection
