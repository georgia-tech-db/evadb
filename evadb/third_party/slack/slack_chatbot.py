SLACK_BOT_TOKEN = "xoxb-5796901551090-5819342908849-iJkccELdXM246Y7SejIYpzsq"
SLACK_APP_TOKEN = "xapp-1-A05Q39W0CBB-5792165989415-e2b813f745b32fc3227e764d2ae62633ca92f2076257801c692b32767ba43f3b"

from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack import WebClient
from slack_bolt import App

# Event API & Web API
app = App(token=SLACK_BOT_TOKEN) 
client = WebClient(SLACK_BOT_TOKEN)

# This gets activated when the bot is tagged in a channel    
@app.event("app_mention")
def handle_message_events(body, logger):
    # Create prompt for ChatGPT
    prompt = str(body["event"]["text"]).split(">")[1]
    
    # Let the user know that we are busy with the request 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Hello from your bot! :robot_face: \nThanks for your request, I'm on it!")

    response = "I got your message: " + prompt
    # Check ChatGPT
    # openai.api_key = OPENAI_API_KEY
    # response = openai.Completion.create(
    #     engine="text-davinci-003",
    #     prompt=prompt,
    #     max_tokens=1024,
    #     n=1,
    #     stop=None,
    #     temperature=0.5).choices[0].text

    # Reply to thread 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Here you go: \n{response}")

# SocketModeHandler(app, SLACK_APP_TOKEN).start()