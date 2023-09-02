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

from evadb.third_party.applications.types import AppHandler, AppHandlerResponse, AppHandlerStatus
from slack_sdk import WebClient

class SlackHandler (AppHandler):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.token = kwargs.get("token")
        self.channel_name = kwargs.get("channel")
    
    def connect(self):
        try:
            self.client = WebClient(token=self.token)
            return AppHandlerStatus(status=True)
        except Exception as e:
            return AppHandlerStatus(status=False, error=str(e))
    
    def disconnect(self):
        """
        TODO: integrate code for disconnecting from slack
        """
        raise NotImplementedError()

    def check_connection(self) -> AppHandlerStatus:
        """
        TODO: integrate code for checking connection to slack
        """
        raise NotImplementedError()

    def get_tables(self) -> AppHandlerResponse:
        """
        TODO: integrate code for getting tables (channels) from slack connection
        """
        raise NotImplementedError()

    def get_columns(self, table_name: str) -> AppHandlerResponse:
        """
        TODO: integrate code for getting columns from slack connection
        """
        raise NotImplementedError()

    def execute_native_query(self, query_string: str) -> AppHandlerResponse:
        """
        TODO: integrate code for executing query on slack
        """
        raise NotImplementedError()