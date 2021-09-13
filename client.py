#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
client.py

Discord Client
"""
import re
import names
import discord
from config import DISCORD_TOKEN, VPN_FILENAME, VPN_SNAPSHOT
from plugins import translate, vultr

class BotClient(discord.Client):
    """
    BotClient
    """

    async def on_ready(self):
        """
        Print after Login
        """
        print("Logged in as", self.user)

    async def on_message(self, message):
        """
        Retrieve on message
        """
        # don't respond to ourselves
        if message.author == self.user:
            return

        # don't listen to DMs
        if isinstance(message.channel, discord.DMChannel):
            return

        channel_name = message.channel.name
        message_content = message.content

        # TranslateBot
        # Translate all messages over general-*
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
                    str(message.author).split("#")[0],
                    channel_name,
                    message_content
                )
                if result:
                    send_channel = discord.utils.get(
                        self.get_all_channels(), name="general-translatebot"
                    )
                    await send_channel.send(result)

        # VPN server for #private-vpn
        if channel_name == "private-vpn":
            if message.content.startswith("-vpn "):
                result = ""
                _command = message.content.split(" ")
                if _command[1] == "list":
                    # List available instances
                    try:
                        result += ":pencil: **List of VPN servers**\n"
                        for _instance in vultr.list_server()['instances']:
                            result += f"       - **{_instance['label']}** http://{_instance['main_ip']}/{VPN_FILENAME}\n"
                    except Exception as e:
                        result = ":warning: Failed to fetch the list."
                elif _command[1] == "open":
                    # Start new server
                    try:
                        vultr.add_server(names.get_full_name().replace(" ", "_"), VPN_SNAPSHOT)
                        result = ":white_check_mark: Done! It may take some time to start server.."
                    except Exception as e:
                        result = ":warning: Failed to start the server."
                elif _command[1] == "stop":
                    # Stop the server
                    try:
                        ret = vultr.delete_server(_command[2])
                        if ret:
                            result = ":white_check_mark: Delete Success! It may take some time to remove the server.."
                        else:
                            result = ":warning: Failed to stop the server."
                    except Exception as e:
                        result = ":warning: Failed to stop the server."
                else:
                    # Help
                    result += ":thinking: List of commands\n"
                    result += "       **-vpn list:** List available servers\n"
                    result += "       **-vpn open:** Open new server\n"
                    result += "       **-vpn stop (name):** Delete server\n"
                await message.channel.send(result)

        # Ping
        # Simple Ping
        if message.content == "-ping":
            await message.channel.send("pong")

if __name__ == "__main__":
    client = BotClient()
    print("Logging in..")
    client.run(DISCORD_TOKEN)

