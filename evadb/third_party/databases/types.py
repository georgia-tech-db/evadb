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
from dataclasses import dataclass
from typing import Generator

import pandas as pd
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.orm import sessionmaker


@dataclass
class DBHandlerResponse:
    """
    Represents the response from a database handler containing data and an optional error message.

    Attributes:
        data (pd.DataFrame): A Pandas DataFrame containing the data retrieved from the database.
        error (str, optional): An optional error message indicating any issues encountered during the operation.
    """

    data: pd.DataFrame
    data_generator: Generator = None
    error: str = None


@dataclass
class DBHandlerStatus:
    """
    Represents the status of a database handler operation, along with an optional error message.

    Attributes:
        status (bool): A boolean indicating the success (True) or failure (False) of the operation.
        error (str, optional): An optional error message providing details about any errors that occurred.
    """

    status: bool
    error: str = None


class DBHandler:
    """
    Base class for handling database operations.

    Args:
        name (str): The name associated with the database handler instance.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.connection = None

    def connect(self):
        """
        Establishes a connection to the database.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def disconnect(self):
        """
        Disconnects from the database.

        This method can be overridden in derived classes to perform specific disconnect actions.
        """
        raise NotImplementedError()

    def get_sqlalchmey_uri(self) -> str:
        """
        Return the valid sqlalchemy uri to connect to the database.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def is_sqlalchmey_compatible(self) -> bool:
        """
        Return  whether the data source is sqlaclchemy compatible

        Returns:
            A True / False boolean value..
        """
        try:
            self.get_sqlalchmey_uri()
        except NotImplementedError:
            return False
        else:
            return True

    def check_connection(self) -> DBHandlerStatus:
        """
        Checks the status of the database connection.

        Returns:
            DBHandlerStatus: An instance of DBHandlerStatus indicating the connection status.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def get_tables(self) -> DBHandlerResponse:
        """
        Retrieves the list of tables from the database.

        Returns:
            DBHandlerResponse: An instance of DBHandlerResponse containing the list of tables or an error message. Data is in a pandas DataFrame.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def get_columns(self, table_name: str) -> DBHandlerResponse:
        """
        Retrieves the columns of a specified table from the database.

        Args:
            table_name (str): The name of the table for which to retrieve columns.

        Returns:
            DBHandlerResponse: An instance of DBHandlerResponse containing the columns or an error message. Data is in a pandas DataFrame. It should have the following two columns: name and dtype. The dtype should be a Python dtype and will default to `str`.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def execute_native_query(self, query_string: str) -> DBHandlerResponse:
        """
        Executes the query through the handler's database engine.

        Args:
            query_string (str): The string representation of the native query.

        Returns:
            DBHandlerResponse: An instance of DBHandlerResponse containing the columns or an error message. Data is in a pandas DataFrame.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def select(self, table_name: str) -> DBHandlerResponse:
        """
        Returns a generator that yields the data from the given table, or the data.
        Args:
            table_name (str): name of the table whose data is to be retrieved.
        Returns:
            DBHandlerResponse: An instance of DBHandlerResponse containing the data, data generator, or an error message. Data is in a pandas DataFrame.

        Raises:
            NotImplementedError: The default implementation of this method is for sqlalchemy-supported data source. The data source that does not support sqlalchemy should overwrite this function.
        """
        try:
            uri = self.get_sqlalchmey_uri()
            # Create a metadata object
            engine = create_engine(uri)
            metadata = MetaData()

            Session = sessionmaker(bind=engine)
            session = Session()
            # Retrieve the SQLAlchemy table object for the existing table
            table_to_read = Table(table_name, metadata, autoload_with=engine)
            # TODO: there is a BUG in the SQLAlchemy session management, when there is a function expression in the plan tree, we will update the catalog for its cost, which leads to a SQLAlchemy deadlock if we return a generator here.
            result = session.execute(table_to_read.select()).fetchall()
            session.close()
            # A generator is better, however, the current implementation suffers from deadlock from different SQLAlchemy sessions.
            return DBHandlerResponse(data=result)
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))
