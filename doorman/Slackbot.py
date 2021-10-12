# -*- coding: utf-8 -*-
from slack import WebClient

import slackbot_setting as ss


class Slackbot:
    """
    Slack bot using slack.WebClient()

    attributes
    ----------
    client: slack.WebClient(your API token)
        your slack web client
    user_dict: dict
        pair of user name and id
    """

    def __init__(self):
        self.client = WebClient(ss.token)
        self.user_dict = self.get_user_dict()
        self.channel_dict = self.get_channel_dict()

    def get_user_dict(self):
        """
        Get the pair of user name and id

        return
        ----------
        user_dict: dict
            Pair of user name and id
        """

        response = self.client.users_list()
        user_dict = {}
        for user in response.data["members"]:
            if user["profile"]["display_name"] == "":
                user_dict[user["profile"]["real_name"]] = user["id"]
            else:
                user_dict[user["profile"]["display_name"]] = user["id"]

        return user_dict

    def get_channel_dict(self):
        """
        Get the pair of channel and id

        return
        ----------
        channel_dict: dict
            Pair of channel and id
        """

        response = self.client.conversations_list(type="public_channel")
        channel_dict = {}
        for channel in response.data["channels"]:
            channel_dict[channel["name"]] = channel["id"]

        return channel_dict

    def send_direct_message(self, username, message):
        """
        Send a direct message

        parameters
        ----------
        username: str
            User name (real_name or display_name)
        message: str
            Message to be posted
        """

        uid = self.user_dict[username]
        self.client.chat_postMessage(channel=uid, text=message)

    def send_message_to_channel(self, channel, message):
        """
        Send a message to channel

        parameters
        ----------
        channel: str
            Channel name
        message: str
            Message to be posted
        """

        cid = self.channel_dict[channel]
        resp = self.client.chat_postMessage(channel=cid, text=message)

        return resp["ok"]
