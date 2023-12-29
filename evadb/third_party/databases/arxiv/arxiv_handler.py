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
import arxiv
import pandas as pd

from evadb.third_party.databases.arxiv.table_column_info import ARXIV_COLUMNS
from evadb.third_party.databases.types import (
    DBHandler,
    DBHandlerResponse,
    DBHandlerStatus,
)


class ArxivHandler(DBHandler):
    def __init__(self, name: str, **kwargs):
        """
        Initialize the handler.
        Args:
            name (str): name of the DB handler instance
            **kwargs: arbitrary keyword arguments for establishing the connection.
        """
        super().__init__(name, **kwargs)
        self.query = kwargs.get("query", "")
        self.max_results = int(kwargs.get("max_results", 0))

    @property
    def supported_table(self):
        def _arxiv_generator():
            for eachRow in self.connection.results(
                arxiv.Search(query=self.query, max_results=self.max_results)
            ):
                yield {
                    property_name: getattr(eachRow, property_name)
                    for property_name, _ in ARXIV_COLUMNS
                }

        mapping = {
            "search_results": {
                "columns": ARXIV_COLUMNS,
                "generator": _arxiv_generator(),
            },
        }
        return mapping

    def connect(self):
        """
        Set up the connection required by the handler.
        Returns:
            DBHandlerStatus
        """
        try:
            self.connection = arxiv.Client()
            return DBHandlerStatus(status=True)
        except Exception as e:
            return DBHandlerStatus(status=False, error=str(e))

    def disconnect(self):
        """
        Close any existing connections.
        """
        pass

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
            return DBHandlerResponse(data=None, error="Not connected to the internet.")

        try:
            tables_df = pd.DataFrame(
                list(self.supported_table.keys()), columns=["table_name"]
            )
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
            columns_df = pd.DataFrame(
                self.supported_table[table_name]["columns"], columns=["name", "dtype"]
            )
            return DBHandlerResponse(data=columns_df)
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))

    def select(self, table_name: str) -> DBHandlerResponse:
        """
        Returns a generator that yields the data from the given table.
        Args:
            table_name (str): name of the table whose data is to be retrieved.
        Returns:
            DBHandlerResponse
        """
        if not self.connection:
            return DBHandlerResponse(data=None, error="Not connected to the database.")
        try:
            if table_name not in self.supported_table:
                return DBHandlerResponse(
                    data=None,
                    error="{} is not supported or does not exist.".format(table_name),
                )
            # TODO: Projection column trimming optimization opportunity
            return DBHandlerResponse(
                data=None,
                data_generator=self.supported_table[table_name]["generator"],
            )
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))
