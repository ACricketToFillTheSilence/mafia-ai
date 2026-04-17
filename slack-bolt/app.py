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

fake_response = """
Horses Mafia

Mafia Members (2 total):
• Stallion Boss (Mob boss) - The alpha horse who commands the herd to eliminate threats from the pasture each night.
• Rogue Mustang (Mafia henchman) - A wild horse who assists the Stallion Boss in driving out one member of the herd each night.

Good Roles (2 total):
• Farrier (Detective) - A skilled horseshoe craftsman who can investigate one horse each night to discover their true nature.
• Veterinarian (Doctor) - A healer who can tend to one horse each night, saving them from the herd's wrath.

Townspeople (4 total):
• Foal (Townspeople) - A young horse with no special abilities.
• Foal (Townspeople) - A young horse with no special abilities.
• Workhorse (Townspeople) - A sturdy horse with no special abilities.
• Workhorse (Townspeople) - A sturdy horse with no special abilities.
"""

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

@app.message("Test")
def message_test(message, say):
    say("This is a test message.")
    parsed_roles =parse_roles_from_response(fake_response)
    for item in parsed_roles:
        say(item)

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
    #response2 = converter.convert(response)
    say(response)



    # Parse out roles from the response and say them in the channel
    #for item in parse_roles_from_response(response):
    #    say(item)

    # Randomly assign roles to users


def parse_roles_from_response(response):
    role_list = []
    # This function should parse the response from the AI and extract the roles and their descriptions.
    for line in response.splitlines():
        print("Here is the current line: " + line)
        line = line.strip()
        if line.startswith("•"):
            print("The line starts with a bullet point, so it is a role.")
            role_info = line[1:].strip()  # Remove the leading '-' and any extra whitespace
            print(role_info)
            role_name = role_info.split(":")[0]  # Split into name and description
            print(role_name)
            role_list.append(role_name.strip())

    return role_list

def assign_roles(users, roles):
    import random

    random.shuffle(roles)
    assigned_roles = {}
    for user, role in zip(users, roles):
        assigned_roles[user] = role
    return assigned_roles

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


