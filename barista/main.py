'''
----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
Robin Scheibler wrote this code.  As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return.               Robin
----------------------------------------------------------------------------

Note
----

At this point we can't have two ssl sockets open at the same time on ESP32 due to memory contraints
https://github.com/micropython/micropython/issues/3650

make sure not to make api call while the real-time api is being used
'''
import gc
import urequests
import time
import json
import os
import re

from uslackclient import SlackClient

from wifi_connect import do_connect
from sensors import read_sensors
from button import button_action

# READ the settings
with open('config.json', 'r') as f:
    config = json.load(f)

do_connect(config['wifi']['SSID'], config['wifi']['pass'])

# instantiate Slack client
slack_client = None
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 2 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "hello"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def help():
    global COMMANDS
    msg = 'Available commands:\n'
    for cmd, params in COMMANDS.items():
        msg += '  {} : {}\n'.format(cmd, params['desc'])
    return msg

COMMANDS = {
        'report' : {
            'action' : lambda : '\n'.join([key + ' : ' + str(val) for key,val in read_sensors().items()]),
            'desc' : 'Reports the temperature and humidity of the lab, and the temperature of the coffee maker hot plate',
            },
        'hello' : {
            'action' : lambda : 'hello you!',
            'desc' : 'The bot will greet you',
            },
        'help' : {
            'action' : help,
            'desc' : 'Prints this help message',
            }
        }

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if "type" in event and event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    for tag, params in COMMANDS.items():
        if command.startswith(tag):
            response = params['action']()

    # Sends the response back to the channel
    slack_client.rtm_send_message(channel, response)

if __name__ == '__main__':

    slack_client = SlackClient(config['slack']['bot_token'])

    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")

        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.server.login_data['self']['id']

        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)

            button_action(slack_client.rtm_send_message, config['button']['channel'], config['button']['message'])
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

