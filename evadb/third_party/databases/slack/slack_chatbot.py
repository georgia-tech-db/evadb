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
import openai
from slack import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from evadb.configuration.configuration_manager import ConfigurationManager

SLACK_BOT_TOKEN = ConfigurationManager().get_value("third_party", "SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = ConfigurationManager().get_value("third_party", "SLACK_APP_TOKEN")
OPENAI_API_KEY = ConfigurationManager().get_value("third_party", "OPENAI_KEY")

# Event API & Web API
app = App(token=SLACK_BOT_TOKEN)
client = WebClient(SLACK_BOT_TOKEN)


# This gets activated when the bot is tagged in a channel
@app.event("app_mention")
def handle_message_events(body, logger):
    # Create prompt for ChatGPT
    prompt = str(body["event"]["text"]).split(">")[1]

    # Let the user know that we are busy with the request
    response = client.chat_postMessage(
        channel=body["event"]["channel"],
        thread_ts=body["event"]["event_ts"],
        text=f'{"Hello from EVADB bot! :robot_face:"}',
    )

    # Check ChatGPT
    openai.api_key = OPENAI_API_KEY
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
    response = client.chat_postMessage(
        channel=body["event"]["channel"],
        thread_ts=body["event"]["event_ts"],
        text=f"{response}",
    )


def create_slack_bot():
    SocketModeHandler(app, SLACK_APP_TOKEN).start()


create_slack_bot()
