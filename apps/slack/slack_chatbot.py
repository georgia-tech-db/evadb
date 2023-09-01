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
import os

import openai
from slack import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.third_party.databases.interface import dynamic_install


class SlackChatbot:
    def __init__(self):
        self.SLACK_BOT_TOKEN = self.verify_and_retreive_token("SLACK_BOT_TOKEN")
        self.SLACK_APP_TOKEN = self.verify_and_retreive_token("SLACK_APP_TOKEN")
        self.OPENAI_API_KEY = self.verify_and_retreive_token("OPENAI_KEY")
        dynamic_install("slack")
        self.create_slack_bot()

    def verify_and_retreive_token(self, token_name: str):
        # Check configuration manager first
        token = ConfigurationManager().get_value("third_party", token_name)

        # If not found, try OS Environment Variable
        if len(token) == 0:
            token = os.environ.get(token_name, "")
        assert (
            len(token) != 0
        ), "Please set the {} in evadb.yml file (under third_party) or set environment variable ({})".format(
            token_name, token_name
        )
        return token_name

    def create_slack_bot(self):
        # Event API & Web API
        self.app = App(token=self.SLACK_BOT_TOKEN)
        self.client = WebClient(self.SLACK_BOT_TOKEN)

        # This gets activated when the bot is tagged in a channel
        @self.app.event("app_mention")
        def handle_message_events(body, logger):
            # Create prompt for ChatGPT
            prompt = str(body["event"]["text"]).split(">")[1]

            # Let the user know that we are busy with the request
            response = self.client.chat_postMessage(
                channel=body["event"]["channel"],
                thread_ts=body["event"]["event_ts"],
                text=f'{"Hello from EVADB bot! :robot_face:"}',
            )

            # Check ChatGPT
            openai.api_key = self.OPENAI_API_KEY
            response = (
                openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
                .choices[0]
                .text
            )

            # Reply to thread
            response = self.client.chat_postMessage(
                channel=body["event"]["channel"],
                thread_ts=body["event"]["event_ts"],
                text=f"{response}",
            )

    def run_slack_bot(self):
        SocketModeHandler(self.app, self.SLACK_APP_TOKEN).start()
