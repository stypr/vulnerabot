#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
client.py

Discord Client
"""
import os
import re
import names
import discord
from discord.ext import commands
from dotenv import load_dotenv
from plugins import translate, vultr, hashcrack

# load envvars
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD = os.getenv("DISCORD_GUILD")
VPN_FILENAME = os.getenv("VPN_FILENAME")
VPN_SNAPSHOT = os.getenv("VPN_SNAPSHOT")

# init bot
help_command = commands.DefaultHelpCommand(no_category="Commands")
bot = commands.Bot(
    command_prefix='-',
    description="https://github.com/stypr/vulnerabot",
    help_command=help_command)

def strip_message(message):
    """ (str) -> str

    Strip emojis and trailing spaces
    Make links click-safe
    """
    message = message.strip()
    message = re.sub("http://", "htt·p://", message)
    message = re.sub("https://", "http·s://", message)
    message = re.sub("<@&.+>", "", message)
    message = re.sub("<@!.+>", "", message)
    message = message.strip()
    return message

@bot.event
async def on_ready():
    print("Logged in!")

@bot.event
async def on_message(message):
    """
    Retrieve messages and process accordingly
    TranslateBot comes here
    """
    # don't respond to ourselves
    if message.author == bot.user:
        return

    # ignore other guilds
    if str(message.guild.id) != DISCORD_GUILD:
        return

    # don't listen to DMs
    if isinstance(message.channel, discord.DMChannel):
        return

    # TranslateBot
    # translate all messages on #general-*
    channel_name = message.channel.name
    message_content = message.content
    if channel_name.startswith("general-") and \
        not channel_name.endswith("translatebot"):
        message_content = strip_message(message_content)

        if message_content:
            result = translate.translate_text(
                str(message.author).split("#")[0],
                channel_name,
                message_content
            )
            if result:
                send_channel = discord.utils.get(
                    bot.get_all_channels(),
                    name="general-translatebot"
                )
                await send_channel.send(result)
                return

    # do some extra stuff here
    await bot.process_commands(message)

@bot.command()
async def crack(ctx, *args):
    """ Hash Crack Command
    Cracks hash by Rainbow Table

    -crack (hash): Cracks MD5, SHA-*, RIPEMD320
    """
    if len(args) != 1:
        result = ":warning: Invalid command. Check -help crack for more information."
    else:
        result = hashcrack.crack_text(args[0])

    await ctx.send(result)

bot.vpn_region = "icn" # default region
@bot.command()
async def vpn(ctx, *args):
    """ VPN Management Command

    -vpn list: List available servers
    -vpn open: Open a new server
    -vpn stop (name): Delete an existing server
    -vpn region: View current region
    -vpn region (location): Set region
    """
    channel_name = ctx.channel.name
    result = ""

    if channel_name != "vpn":
        result = ":warning: You don't have the permission to access this command."
        await ctx.send(result)
        return

    if args[0] not in ("list", "open", "stop", "region"):
        result = ":warning: Invalid command. Check -help vpn for more information."
        await ctx.send(result)
        return

    if args[0] == "list":
        result = ":pencil: **List of VPN servers**\n"
        try:
            for _instance in vultr.list_server()['instances']:
                result += f"  - **{_instance['label']}**: http://{_instance['main_ip']}/{VPN_FILENAME}\n"
        except:
            result = ":warning: Failed to fetch the list."

    if args[0] == "stop":
        if len(args) == 2:
            try:
                ret = vultr.delete_server(args[1])
                if ret:
                    result = ":white_check_mark: Delete successful! It may take some time to remove the server.."
                else:
                    result = ":warning: Failed to stop the server."
            except:
                result = ":warning: Failed to stop the server."

    if args[0] == "open":
        if len(args) != 2:
            try:
                vultr.add_server(names.get_full_name().replace(" ", "_"), VPN_SNAPSHOT, bot.vpn_region)
                result = ":white_check_mark: Open successful! It may take some time to start server.."
            except:
                result = ":warning: Failed to start the server."

    if args[0] == "region":
        if len(args) == 2:
            if args[1] in ("nrt", "icn", "sgp", "lax", "sjc"):
                bot.vpn_region = args[1]
                result = f":white_check_mark: Region set to {bot.vpn_region}!"
            else:
                result = ":warning: Invalid Region! (Available: nrt, icn, sgp, lax, sjc)"
        else:
            result = f":map: Current region is **{bot.vpn_region}*.*"

    await ctx.send(result)

@bot.command()
async def ping(ctx):
    """ Replies pong message """
    await ctx.send('pong')

if __name__ == "__main__":
    print("Logging in..")
    bot.run(DISCORD_TOKEN)
