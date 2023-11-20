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

from requests_html import HTMLSession
import json
import pandas as pd

from evadb.third_party.databases.hackernews.table_column_info import *
from evadb.third_party.databases.types import (
    DBHandler,
    DBHandlerResponse,
    DBHandlerStatus,
)


class HackerNewsHandler(DBHandler):
    def __init__(self, name: str, **kwargs):
        """
        Initialize the handler.
        Args:
            name (str): name of the DB handler instance
            **kwargs: arbitrary keyword arguments for establishing the connection.
        """
        super().__init__(name)

        self.max_item = int(kwargs.get("maxitem", False))   # Limits the number of rows for the table items

        self.tables = [
            "items", "users", "top_stories", 
            "new_stories", "best_stories", "ask_stories", 
            "show_stories", "job_stories", "updates"
        ]

        # Define columns
        item = [
                col_id, col_deleted, col_type, col_by, col_time, 
                col_text, col_dead, col_parent, col_poll, col_kids, 
                col_url, col_score, col_title, col_parts, col_descendants
        ]
        user = [col_id, col_created, col_karma, col_about, col_submitted]
        self.columns = {
            "items": item,
            "top_stories": item,
            "new_stories": item,
            "best_stories": item,
            "ask_stories": item,
            "show_stories": item,
            "job_stories": item,
            "users": user,
            "updates": [col_items, col_profiles],
        }

    def connect(self):
        """
        Set up the connection required by the handler.
        Returns:
            DBHandlerStatus
        """
        try:
            self.connection = HTMLSession()
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
            return DBHandlerResponse(data=None, error="Not connected to the database.")

        try:
            tables_df = pd.DataFrame(
                self.tables, columns=["table_name"]
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
        if table_name not in self.tables:
            return DBHandlerResponse(
                data=None,
                error="{} is not supported or does not exist.".format(table_name),
            )
        try:
            columns_df = pd.DataFrame(
                self.columns[table_name], columns=["name", "dtype"]
            )
            return DBHandlerResponse(data=columns_df)
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))


    def _fetch_json_data(self, key):
        """
        Fetch data from a URL and return it as a JSON object
        """
        url = "https://hacker-news.firebaseio.com/v0/{}.json?print=pretty".format(key)
        response = self.connection.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data
        else:
            return None

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
        if table_name not in self.tables:
            return DBHandlerResponse(
                data=None,
                error="{} is not supported or does not exist.".format(table_name),
            )
        if(not self.max_item):
            self.max_item = self._fetch_json_data("maxitem")
        try:
            def _item_generator():
                # Get all items from 1 to max_item
                for index in range(1, self.max_item+1):
                    row = self._fetch_json_data("item/{}".format(index))
                    if row:
                        yield {
                            column_name: row[column_name]
                            if column_name in row.keys() else None
                            for column_name, _ in self.columns[table_name]
                        }

            def _user_generator():
                visited = set()
                # Search all valid users that created the items from 1 to max_item
                for index in range(1, self.max_item+1):
                    username = self._fetch_json_data("item/{}".format(index))["by"]
                    if username not in visited:
                        visited.add(username)
                        row = self._fetch_json_data("user/{}".format(username))
                        if row:
                            yield {
                                column_name: row[column_name]
                                if column_name in row.keys() else None
                                for column_name, _ in self.columns[table_name]
                            }

            def _updates_generator():
                """
                Generator function for the updates table
                """
                row = self._fetch_json_data("updates")
                if row:
                    yield {
                        column_name: row[column_name]
                        if column_name in row.keys() else None
                        for column_name, _ in self.columns[table_name]
                    }

            def _catalog_generator():
                """
                Generator function for top_stories, new_stories, best_stores and
                ask_stories
                """
                table_map = {
                    "top_stories": "topstories",
                    "new_stories": "newstories",
                    "best_stories": "beststories",
                    "ask_stories": "askstories",
                    "show_stories": "showstories",
                    "job_stories": "jobstories"
                }

                indexes = self._fetch_json_data(table_map[table_name])
                for index in indexes:
                    row = self._fetch_json_data("item/{}".format(index))
                    if row:
                        yield {
                            column_name: row[column_name]
                            if column_name in row.keys() else None
                            for column_name, _ in self.columns[table_name]
                        }

            if (table_name == "items"):
                generator = _item_generator
            elif (table_name == "users"):
                generator = _user_generator
            elif (table_name == "updates"):
                generator = _updates_generator
            else:
                generator = _catalog_generator

            return DBHandlerResponse(
                data=None,
                data_generator=generator(),
            )

        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))
