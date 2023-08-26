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
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")
        self.user = kwargs.get("user")
        self.token = kwargs.get("token")
        self.channel = kwargs.get("channel")

    def connect(self):
        self.client = WebClient(token=self.token)

    def post_message (self, message) -> DBHandlerResponse:
        try:
            response = self.client.chat_postMessage(channel=self.channel, text=message)
            return DBHandlerResponse(data=response["message"]["text"])
        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            return DBHandlerResponse(data=None, error=e.response['error'])

    def get_messages (self) -> DBHandlerResponse:
        return DBHandlerResponse(data=self.client.conversations_history(channel=self.channel))
