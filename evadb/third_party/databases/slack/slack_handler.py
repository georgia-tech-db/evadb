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
import pandas as pd
import certifi
import ssl
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from evadb.third_party.databases.types import (
    DBHandler,
    DBHandlerResponse,
    DBHandlerStatus,
)


class SlackHandler(DBHandler):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.token = kwargs.get("token")
        self.channel_name = kwargs.get("channel")

    def connect(self):
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            self.client = WebClient(token=self.token, ssl=ssl_context)
            return DBHandlerStatus(status=True)
        except Exception as e:
            return DBHandlerStatus(status=False, error=str(e))

    def disconnect(self):
        
        pass

    def check_connection(self) -> DBHandlerStatus:
        try:
            self.client.api_test()
        except SlackApiError as e:
            assert e.response["ok"] is False
            return False
        return True
    
    def channel_list(self):
        channels_list = {}
        if self.client:
            channels = self.client.conversations_list(
                types="public_channel,private_channel"
            )["channels"]
            # self.channel_names = [c["name"] for c in channels]
            for c in channels:
                channels_list[c["name"]] = c["id"]
        return channels_list
    

    def get_tables(self) -> DBHandlerResponse:
        if self.client:
            channels = self.client.conversations_list(
                types="public_channel,private_channel"
            )["channels"]
            self.channel_names = [c["name"] for c in channels]
            tables_df = pd.DataFrame(self.channel_names, columns=["table_name"])
            return DBHandlerResponse(data=tables_df)
        
    def get_columns(self, table_name: str) -> DBHandlerResponse:
        columns = [
            ["ts", str],
            ["text", str],
            ["user",str],
            ["channel", str],
            ["reactions", str],
            ["attachments", str],
            ["thread_ts", str],
            ["reply_count", str],
            ["reply_users_count", str],
            ["latest_reply", str],
            ["subtype", str],
            ["hidden", str],
        ]
        columns_df = pd.DataFrame(columns, columns=["name", "dtype"])
        return DBHandlerResponse(data=columns_df)

    def post_message(self, message) -> DBHandlerResponse:
        try:
            response = self.client.chat_postMessage(channel=self.channel, text=message)
            return DBHandlerResponse(data=response["message"]["text"])
        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            return DBHandlerResponse(data=None, error=e.response["error"])

    def _convert_json_response_to_DataFrame(self, json_response):
        messages = json_response["messages"]
        columns = ["text", "ts", "user"]
        data_df = pd.DataFrame(columns=columns)
        for message in messages:
            if message["text"] and message["ts"] and message["user"]:
                data_df.loc[len(data_df.index)] = [
                    message["text"],
                    message["ts"],
                    message["user"],
                ]
        return data_df

    def get_messages(self) -> DBHandlerResponse:
        try:
            channels = self.client.conversations_list(
                types="public_channel,private_channel"
            )["channels"]
            channel_ids = {c["name"]: c["id"] for c in channels}
            response = self.client.conversations_history(
                channel=channel_ids[self.channel_name]
            )
            data_df = self._convert_json_response_to_DataFrame(response)
            return data_df

        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            return DBHandlerResponse(data=None, error=e.response["error"])

    def del_message(self, timestamp) -> DBHandlerResponse:
        try:
            self.client.chat_delete(channel=self.channel, ts=timestamp)
        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            return DBHandlerResponse(data=None, error=e.response["error"])

    def supported_table(self, channel):
        def slack_generator():
            channel_list = self.channel_list()
            for message in self.client.conversations_history(channel=channel_list[channel])["messages"]:
                if message["type"] == "message":
                    yield {
                        "user": message.get("user", "N/A"),
                        "ts": message.get("ts", "N/A"),
                        "text": message.get("text", "N/A"),
                        "channel": message.get("channel", "N/A"),
                        "reactions": message.get("reactions", "N/A"),
                        "attachments": message.get("attachments", "N/A"),
                        "thread_ts": message.get("thread_ts", "N/A"),
                        "reply_count": message.get("reply_count", "N/A"),
                        "reply_users_count": message.get("reply_users_count", "N/A"),
                        "latest_reply": message.get("latest_reply", "N/A"),
                        "subtype": message.get("subtype", "N/A"),
                        "hidden": message.get("hidden", "N/A"),
                    }

        mapping = {
            "random": {
                "columns": ["user", "ts", "text", "channel", "reactions", "attachments", "thread_ts",
                             "reply_count", "reply_users_count", "latest_reply", "subtype", "hidden"], 
                "generator": slack_generator(),
            },
        }
        return mapping
        
    def select(self, table_name: str) -> DBHandlerResponse:
        """
        Returns a generator that yields the data from the given table.
        Args:
            table_name (str): name of the table whose data is to be retrieved.
        Returns:
            DBHandlerResponse
        """


        if not self.client:
            return DBHandlerResponse(data=None, error="Not connected to the database.")
        try:
            table = self.supported_table(channel=table_name)
            return DBHandlerResponse(
                data=None,
                data_generator=table["random"]["generator"],
            )
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))

