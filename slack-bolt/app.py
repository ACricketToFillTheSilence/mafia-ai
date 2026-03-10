import os

from markdown_to_mrkdwn import SlackMarkdownConverter

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from ai.ai_constants import GAME_MASTER_SYSTEM_CONTENT
from ai.anthropic import AnthropicAPI
from mafia_queries import get_provider_response

# This sample slack application uses SocketMode
# For the companion getting started setup guide,
# see: https://docs.slack.dev/tools/bolt-python/getting-started

# Initializes your app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

converter = SlackMarkdownConverter()


# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click",
                },
            }
        ],
        text=f"Hey there <@{message['user']}>!",
    )

@app.message("Mafia")
def message_new_game(message, say):
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Can you tell me more about the game you'd like to play?"},
            },
            {
            	"type": "input",
                "block_id": "my_input_block_id",
			    "element": {
				    "type": "plain_text_input",
				    "action_id": "plain_text_input-action"
			    },
			    "label": {
				    "type": "plain_text",
				    "text": "Theme",
				    "emoji": True
			    },
			    "optional": False
            },
            {
			    "type": "section",
                "block_id": "multi_users_select",
			    "text": {
				    "type": "mrkdwn",
				    "text": "Add specific users to the game."
			    },
			    "accessory": {
				    "type": "multi_users_select",
				    "placeholder": {
					    "type": "plain_text",
					    "text": "Select users",
					    "emoji": True
				    },
				    "action_id": "users_select-action"
                }
            },
            {
			    "type": "actions",
			    "elements": [
			        {
					    "type": "button",
					    "text": {
						    "type": "plain_text",
						    "text": "Submit",
						    "emoji": True
					    },
					    "value": "click_me_123",
					    "action_id": "actionId-0"
				}
			]
		},
        ],
        text=f"Starting a new game of Mafia!",
    )


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")

@app.action("users_select-action")
def handle_users_select(body, ack, say):
    ack()
    selected_users = body['actions'][0]['selected_users']
    selected_users_mentions = ", ".join([f"<@{user_id}>" for user_id in selected_users])
    say(f"<@{body['user']['id']}> selected the following users: {selected_users_mentions}")

@app.action("actionId-0")
def handle_plain_text_input(body, ack, say, message):
    ack()

    # Access the submitted values from the input block
    stateValues = body['state']['values']
    # Access the value using the block_id and action_id
    submittedString = stateValues['my_input_block_id']['plain_text_input-action']['value']

    # Access the selected number of players
    numberOfPlayers = len(stateValues['multi_users_select']['users_select-action']['selected_users'])
    response = get_provider_response(
        user_id=body['user']['id'],
        prompt=submittedString.split(),
        # To add in more variables, add the variable in the ai_constants file and then add the variable as an argument here.
        system_content=str.format(GAME_MASTER_SYSTEM_CONTENT, num_players=numberOfPlayers),
    )
    response = converter.convert(response)
    say(response)
    #say(f"<@{body['user']['id']}> submitted the theme: {submittedString}")



# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
