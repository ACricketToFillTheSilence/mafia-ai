import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# This sample slack application uses SocketMode
# For the companion getting started setup guide,
# see: https://docs.slack.dev/tools/bolt-python/getting-started

# Initializes your app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


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
                "text": {"type": "mrkdwn", "text": "What is the theme?"},
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
				    "text": "Label",
				    "emoji": True
			    },
			    "optional": False
            },
            {
			    "type": "actions",
			    "elements": [
			        {
					    "type": "button",
					    "text": {
						    "type": "plain_text",
						    "text": "Click Me",
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

@app.action("actionId-0")
def handle_plain_text_input(body, ack, say, message):
    ack()

    # Access the submitted values from the input block
    stateValues = body['state']['values']
    # Access the value using the block_id and action_id
    submittedString = stateValues['my_input_block_id']['plain_text_input-action']['value']
    print("Submitted string:", submittedString)
    say(f"<@{body['user']['id']}> submitted the theme: {submittedString}")


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
