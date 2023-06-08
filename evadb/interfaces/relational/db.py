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
import asyncio

import pandas

from evadb.configuration.constants import EvaDB_DATABASE_DIR
from evadb.database import EvaDBDatabase, init_evadb_instance
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.interfaces.relational.relation import EvaDBQuery
from evadb.interfaces.relational.utils import execute_statement, try_binding
from evadb.models.server.response import Response
from evadb.models.storage.batch import Batch
from evadb.parser.alias import Alias
from evadb.parser.select_statement import SelectStatement
from evadb.parser.utils import (
    parse_create_udf,
    parse_create_vector_index,
    parse_drop_index,
    parse_drop_table,
    parse_drop_udf,
    parse_load,
    parse_query,
    parse_table_clause,
)
from evadb.udfs.udf_bootstrap_queries import init_builtin_udfs
from evadb.utils.logging_manager import logger


class EvaDBConnection:
    def __init__(self, evadb: EvaDBDatabase, reader, writer):
        self._reader = reader
        self._writer = writer
        self._cursor = None
        self._result: Batch = None
        self._evadb = evadb

    def cursor(self):
        """Retrieves a cursor associated with the connection.

        Returns:
            EvaDBCursor: The cursor object used to execute queries.


        Examples:
            >>> import evadb
            >>> connection = connect()
            >>> cursor = connection.cursor()
        """
        # One unique cursor for one connection
        if self._cursor is None:
            self._cursor = EvaDBCursor(self)
        return self._cursor


class EvaDBCursor(object):
    def __init__(self, connection):
        self._connection = connection
        self._evadb = connection._evadb
        self._pending_query = False
        self._result = None

    async def execute_async(self, query: str):
        """
        Send query to the EvaDB server.
        """
        if self._pending_query:
            raise SystemError(
                "EvaDB does not support concurrent queries. \
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

    def table(self, table_name: str) -> EvaDBQuery:
        """
        Retrieves data from a table in the database.

        Args:
            table_name (str): Name of the table.

        Returns:
            EvaDBQuery: The EvaDBQuery object representing the table query.

        Examples:
            >>> relation = conn.table("sample_table")
        """
        table = parse_table_clause(table_name)
        # SELECT * FROM table
        select_stmt = SelectStatement(
            target_list=[TupleValueExpression(col_name="*")], from_table=table
        )
        try_binding(self._evadb.catalog, select_stmt)
        return EvaDBQuery(self._evadb, select_stmt, alias=Alias(table_name.lower()))

    def df(self) -> pandas.DataFrame:
        """
        Returns the result as a pandas DataFrame.

        Returns:
            pandas.DataFrame: The result as a DataFrame.

        Raises:
            Exception: If no valid result is available with the current connection.

        Examples:
            >>> result = conn.query("CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;").df()
        """
        if not self._result:
            raise Exception("No valid result with the current cursor")
        return self._result.frames

    def create_vector_index(
        self, index_name: str, table_name: str, expr: str, using: str
    ) -> "EvaDBCursor":
        """
        Creates a vector index using the provided expr on the table.

        Args:
            index_name (str): Name of the index.
            table_name (str): Name of the table.
            expr (str): Expression used to build the vector index.
            using (str): Method used for indexing, can be `FAISS` or `QDRANT`.

        Returns:
            EvaDBCursor: The EvaDBCursor object.

        Examples:
            Create a Vector Index using QDRANT

            >>> conn.create_vector_index(
                    "faiss_index",
                    table_name="meme_images",
                    expr="SiftFeatureExtractor(data)",
                    using="QDRANT"
                )
        """
        stmt = parse_create_vector_index(index_name, table_name, expr, using)
        self._result = execute_statement(self._evadb, stmt)
        return self

    def load(
        self, file_regex: str, table_name: str, format: str, **kwargs
    ) -> EvaDBQuery:
        """
        Loads data from files into a table.

        Args:
            file_regex (str): Regular expression specifying the files to load.
            table_name (str): Name of the table.
            format (str): File format of the data.
            **kwargs: Additional keyword arguments for configuring the load operation.

        Returns:
            EvaDBQuery: The EvaDBQuery object representing the load query.

        Examples:
            Load the online_video.mp4 file into table named 'youtube_video'.

            >>> conn.load("online_video.mp4", "youtube_video", "video")
        """
        # LOAD {FORMAT} file_regex INTO table_name
        stmt = parse_load(table_name, file_regex, format, **kwargs)
        return EvaDBQuery(self._evadb, stmt)

    def drop_table(self, table_name: str, if_exists: bool = True) -> "EvaDBQuery":
        """
        Drop a table in the database.

        Args:
            table_name (str): Name of the table to be dropped.
            if_exists (bool): If True, do not raise an error if the Table does not already exist. If False, raise an error.

        Returns:
            EvaDBQuery: The EvaDBQuery object representing the DROP TABLE.

        Examples:
            Drop table 'sample_table'

            >>> conn.drop_table("sample_table", if_exists = True)
        """
        stmt = parse_drop_table(table_name, if_exists)
        return EvaDBQuery(self._evadb, stmt)

    def drop_udf(self, udf_name: str, if_exists: bool = True) -> "EvaDBQuery":
        """
        Drop a udf in the database.

        Args:
            udf_name (str): Name of the udf to be dropped.
            if_exists (bool): If True, do not raise an error if the UDF does not already exist. If False, raise an error.

        Returns:
            EvaDBQuery: The EvaDBQuery object representing the DROP UDF.

        Examples:
            Drop UDF 'ObjectDetector'

            >>> conn.drop_udf("ObjectDetector", if_exists = True)
        """
        stmt = parse_drop_udf(udf_name, if_exists)
        return EvaDBQuery(self._evadb, stmt)

    def drop_index(self, index_name: str, if_exists: bool = True) -> "EvaDBQuery":
        """
        Drop an index in the database.

        Args:
            index_name (str): Name of the index to be dropped.
            if_exists (bool): If True, do not raise an error if the index does not already exist. If False, raise an error.

        Returns:
            EvaDBQuery: The EvaDBQuery object representing the DROP INDEX.

        Examples:
            Drop the index with name 'faiss_index'

            >>> conn.drop_index("faiss_index", if_exists = True)
        """
        stmt = parse_drop_index(index_name, if_exists)
        return EvaDBQuery(self._evadb, stmt)

    def create_udf(
        self,
        udf_name: str,
        if_not_exists: bool = True,
        impl_path: str = None,
        type: str = None,
        **kwargs
    ) -> "EvaDBQuery":
        """
        Create a udf in the database.

        Args:
            udf_name (str): Name of the udf to be created.
            if_not_exists (bool): If True, do not raise an error if the UDF already exist. If False, raise an error.
            impl_path (str): Path string to udf's implementation.
            type (str): Type of the udf (e.g. HuggingFace).
            **kwargs: Additional keyword arguments for configuring the create udf operation.

        Returns:
            EvaDBQuery: The EvaDBQuery object representing the UDF created.

        Examples:
            >>> conn.create_udf("MnistImageClassifier", if_exists = True, 'mnist_image_classifier.py')
        """
        stmt = parse_create_udf(udf_name, if_not_exists, impl_path, type, **kwargs)
        return EvaDBQuery(self._evadb, stmt)

    def query(self, sql_query: str) -> EvaDBQuery:
        """
        Executes a SQL query.

        Args:
            sql_query (str): The SQL query to be executed

        Returns:
            EvaDBQuery: The EvaDBQuery object.

        Examples:
            >>> conn.query("DROP UDF IF EXISTS SentenceFeatureExtractor;")
        """
        stmt = parse_query(sql_query)
        return EvaDBQuery(self._evadb, stmt)


def connect(
    evadb_dir: str = EvaDB_DATABASE_DIR, sql_backend: str = None
) -> EvaDBConnection:
    """
    Connects to the EvaDB server and returns a connection object.

    Args:
        evadb_dir (str): The directory used by EvaDB to store database-related content. Default is "evadb".
        sql_backend (str): Custom database URI to be used. We follow the SQLAlchemy database URL format.
            Default is SQLite in the EvaDB directory. See https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls.

    Returns:
        EvaDBConnection: A connection object representing the connection to the EvaDB database.

    Examples:
        >>> from evadb import connect
        >>> conn = connect()
    """

    # As we are not employing a client-server approach for the Pythonic interface, the
    # host and port parameters are irrelevant. Additionally, for the EvaDBConnection, the
    # reader and writer parameters are not relevant in the serverless approach.
    evadb = init_evadb_instance(evadb_dir, custom_db_uri=sql_backend)
    init_builtin_udfs(evadb, mode="release")
    return EvaDBConnection(evadb, None, None)


# WIP
# support remote connections from pythonic APIs


async def get_connection(host: str, port: int) -> EvaDBConnection:
    reader, writer = await asyncio.open_connection(host, port)
    # no db required for remote connection
    connection = EvaDBConnection(None, reader, writer)
    return connection


def connect_remote(host: str, port: int) -> EvaDBConnection:
    connection = asyncio.run(get_connection(host, port))
    return connection
