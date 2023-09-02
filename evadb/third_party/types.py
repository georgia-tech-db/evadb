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


@dataclass
class ThirdPartyResponse:
    """
    Represents the response from a third party service handler
    """

    pass


@dataclass
class ThirdPartyStatus:
    """
    Represents the status of a third party service handler operation
    """

    pass


class ThirdPartyHandler:
    """
    Base class for handling third party service operations.

    Args:
        name (str): The name associated with the database handler instance.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.connection = None

    def connect(self):
        """
        Establishes a connection to the third party service.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def disconnect(self):
        """
        Disconnects from the third party service.

        This method can be overridden in derived classes to perform specific disconnect actions.
        """
        raise NotImplementedError()

    def check_connection(self) -> ThirdPartyStatus:
        """
        Checks the status of the connection.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def get_tables(self) -> ThirdPartyResponse:
        """
        Retrieves the list of tables.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def get_columns(self, table_name: str) -> ThirdPartyResponse:
        """
        Retrieves the columns of a specified table.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()

    def execute_native_query(self, query_string: str) -> ThirdPartyResponse:
        """
        Executes the query through the handler's engine.

        Raises:
            NotImplementedError: This method should be implemented in derived classes.
        """
        raise NotImplementedError()
