#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
client.py

Discord Client
"""
import re
import discord
from config import DISCORD_TOKEN
from plugins import translate

class BotClient(discord.Client):
    """
    BotClient
    """

    async def on_ready(self):
        """
        Print after Login
        """
        print("Logged on as", self.user)

    async def on_message(self, message):
        """
        Retrieve on message
        """
        # don't respond to ourselves
        if message.author == self.user:
            return

        # TranslateBot
        # Translate all messages over general-*
        channel_name = message.channel.name
        if channel_name.startswith("general-") and "translate" not in channel_name:
            # Strip some messages
            message_content = message.content
            message_content = message_content.strip()
            message_content = re.sub("http://", "htt·p://", message_content)
            message_content = re.sub("https://", "http·s://", message_content)
            message_content = re.sub("<@&.+>", "", message_content)
            message_content = re.sub("<@!.+>", "", message_content)
            message_content = message_content.strip()
            # Translate and send message
            if message_content:
                result = translate.translate_text(
                    message.author,
                    channel_name,
                    message_content
                )
                if result:
                    send_channel = discord.utils.get(
                        self.get_all_channels(), name="general-translatebot"
                    )
                    await send_channel.send(result)

        # Ping
        # Simple Ping
        if message.content == "ping":
            await message.channel.send("pong")


if __name__ == "__main__":
    client = BotClient()
    print("Logging in..")
    client.run(DISCORD_TOKEN)
