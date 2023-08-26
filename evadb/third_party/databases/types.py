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

import pandas as pd


@dataclass
class DBHandlerResponse:
    """
    Represents the response from a database handler containing data and an optional error message.

    Attributes:
        data (pd.DataFrame): A Pandas DataFrame containing the data retrieved from the database.
        error (str, optional): An optional error message indicating any issues encountered during the operation.
    """

    data: pd.DataFrame
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
            DBHandlerResponse: An instance of DBHandlerResponse containing the columns or an error message. Data is in a pandas DataFrame.

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
