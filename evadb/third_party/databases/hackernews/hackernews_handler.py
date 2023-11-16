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
import json

import pandas as pd
import requests

from evadb.third_party.databases.hackernews.table_column_info import HACKERNEWS_COLUMNS
from evadb.third_party.databases.types import (
    DBHandler,
    DBHandlerResponse,
    DBHandlerStatus,
)


class HackernewsSearchHandler(DBHandler):
    def connection ():
        return requests.get("https://www.google.com/").status_code == 200

    def __init__(self, name: str, **kwargs):
        """
        Initialize the handler.
        Args:
            name (str): name of the DB handler instance
            **kwargs: arbitrary keyword arguments for establishing the connection.
        """
        super().__init__(name)
        self.query = kwargs.get("query", "")
        self.tags = kwargs.get("tags", "")

    @property
    def supported_table(self):
        def _hackernews_topics_generator():
            url = "http://hn.algolia.com/api/v1/search?"
            url += "query=" + self.query
            url += "&tags=" + (
                "story" if self.tags == "" else +self.tags
            )  # search stories by default
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("Could not reach website.")
            json_result = response.content
            dict_result = json.loads(json_result)
            for row in dict_result:
                yield {
                    property_name: row[property_name]
                    for property_name, _ in HACKERNEWS_COLUMNS
                }

        mapping = {
            "search_results": {
                "columns": HACKERNEWS_COLUMNS,
                "generator": _hackernews_topics_generator(),
            },
        }
        return mapping

    def connect(self):
        """
        Set up the connection required by the handler.
        Returns:
            DBHandlerStatus
        """
        return DBHandlerStatus(status=True)

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
        if self.connection():
            return DBHandlerStatus(status=True)
        else:
            return DBHandlerStatus(status=False, error="Not connected to the internet.")

    def get_tables(self) -> DBHandlerResponse:
        """
        Return the list of tables in the database.
        Returns:
            DBHandlerResponse
        """
        if not self.connection():
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
        if not self.connection():
            return DBHandlerResponse(data=None, error="Not connected to the internet.")
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

            return DBHandlerResponse(
                data=None,
                data_generator=self.supported_table[table_name]["generator"],
            )
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))
