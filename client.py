#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
client.py

Discord Client
"""
import datetime
import os
import re
from io import BytesIO
import names
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from plugins import translate, vultr, hashcrack, dbleak
from plugins.vendor.dns.whois.DomainProtocol import DomainQuery

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

@tasks.loop(hours=24)
async def statusbot():
    """
    statusbot
    """

    # send messages to get_channel
    status_channel = discord.utils.get(
        bot.get_all_channels(),
        name="status"
    )

    # get domain expiration status
    message = status_channel.get_partial_message(937210067785224242)
    result = ":link: **Domain List**\n\n"
    domain_list = [
        "harold.kim",
        "stypr.com",
        "eagle-jump.org",
        "fe.gy",
        "stypr.com",
    ]
    for domain in domain_list:
        try:
            domain_result = DomainQuery.query_domain(domain, 3000)
            result += f"**{domain}**: "
            # result += f"({domain_result['expiry']}): "
            result += f"{domain_result['expiry_message']}\n"
            if ("imfast.kr") in domain:
                result = result.replace(domain, "[redacted].kr")
        except:
            pass

    result += "\nLast Updated at " + str(datetime.datetime.now())
    await message.edit(content=result)
    # reserved
    # message = status_channel.get_partial_message(937210069483941929)
    # await message.edit(content="Reserved")

@tasks.loop(minutes=1)
async def cctvbot():
    """
    cctvbot
    """

    temp_cctv_size = int(os.popen("ls -al /mnt/usb/cctv/ 2>&1 | wc -l").read().strip())
    try:
        curr_cctv_size = int(open("/tmp/cctv_size", "rb").read().strip())
    except:
        curr_cctv_size = 0

    if temp_cctv_size != curr_cctv_size:
        motion_detected = True
        f = open("/tmp/cctv_size", "w")
        f.write(str(temp_cctv_size))
        f.close()
    else:
        motion_detected = False

    if motion_detected:
        # send messages to get_channel
        general_channel = discord.utils.get(
            bot.get_all_channels(),
            name="cctv"
        )
        result = f":warning: cctvbot: hey <@346163688102821888>, motion detected! (curr:{temp_cctv_size} != prev:{curr_cctv_size})"
        await general_channel.send(result)

@bot.event
async def on_ready():
    """
    Logged in check
    """
    cctvbot.start()
    statusbot.start()
    print("Logged in!")

bot.curr_translate_secret = ""
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
            if not bot.curr_translate_secret:
                bot.curr_translate_secret = translate.get_secret()
                print(f"Current Secret: {bot.curr_translate_secret}")

            result = translate.translate_text(
                str(message.author).split("#", maxsplit=1)[0],
                channel_name,
                message_content,
                bot.curr_translate_secret
            )
            if result:
                send_channel = discord.utils.get(
                    bot.get_all_channels(),
                    name="general-translatebot"
                )
                await send_channel.send(result)

    # do some extra stuff here
    await bot.process_commands(message)

@bot.command()
async def crack(ctx, *args):
    """ Cracking different hashes by rainbow table

    -crack (hash): Cracks MD5, SHA-*, RIPEMD320
    """
    if len(args) != 1:
        result = ":warning: Invalid command. Check -help crack for more information."
    else:
        result = hashcrack.crack_text(args[0])

    await ctx.send(result)

@bot.command()
async def leak(ctx, *args):
    """ Find account credentials from breached databases. (for #donator)

    -leak account (email_address)
    -leak domain (domain)
    """
    channel_name = ctx.channel.name
    result = ""

    if channel_name not in ("donator", "vpn"):
        result = ":warning: You don't have the permission to access this command."
        await ctx.send(result)
        return

    if args[0] not in ("account", "domain"):
        result = ":warning: Invalid command. Check -help leak for more information."
        await ctx.send(result)
        return

    if args[0] == "account":
        result = ":detective: **List of breached accounts**\n"
        result += dbleak.find_account(args[1], threshold=10)
        await ctx.send(result)

    if args[0] == "domain":
        result = ":detective: **List of breached accounts**\n"
        await ctx.send(result)
        result = dbleak.find_domain(args[1], threshold=200)
        await ctx.send(file=discord.File(BytesIO(result.encode()), 'domain_output.csv'))

bot.vpn_region = "icn" # default region
@bot.command()
async def vpn(ctx, *args):
    """ VPN management (for #vpn)

    -vpn list: List available servers
    -vpn open: Open a new server
    -vpn stop (name): Delete an existing server
    -vpn region: View current region
    -vpn region (location): Set region
    """
    channel_name = ctx.channel.name
    result = ""

    if channel_name not in ("vpn"):
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

    temp_gpu = os.popen("/opt/vc/bin/vcgencmd measure_temp").read().strip()
    temp_cpu = os.popen("cat /sys/class/thermal/thermal_zone0/temp").read().strip()
    pc_uptime = os.popen("uptime").read().strip()

    result = f"**GPU:** {temp_gpu.split('temp=')[1]} / **CPU**: {round(float(temp_cpu)/1000.0,1)}'C\n"
    result += f"**Uptime:** {pc_uptime}"
    await ctx.send(result)

@bot.command()
async def cctv(ctx, *args):
    """ CCTV control menu (for #cctv)

    -cctv start
    -cctv stop
    -cctv restart
    -cctv status
    """
    channel_name = ctx.channel.name
    result = ""

    if channel_name not in ("cctv"):
        result = ":warning: You don't have the permission to access this command."
        await ctx.send(result)
        return

    if args[0] not in ("start", "stop", "restart", "status"):
        result = ":warning: Invalid command. Check -help vpn for more information."
        await ctx.send(result)
        return

    if args[0] == "start":
        res = os.popen("sudo systemctl start motion.service 2>&1").read()
        result = ":white_check_mark: Start Successful!"

    if args[0] == "stop":
        res = os.popen("sudo systemctl stop motion.service 2>&1").read()
        result = ":white_check_mark: Stop Successful!"

    if args[0] == "restart":
        res = os.popen("sudo systemctl restart motion.service 2>&1").read()
        result = ":white_check_mark: Stop Successful!"

    if args[0] == "status":
        res = os.popen("sudo systemctl status motion.service 2>&1").read()
        result = ":white_check_mark: Service Status\n"
        result += f"```\n{res}```"

    await ctx.send(result)

@bot.command()
async def trans(ctx, *args):
    """ Configure translatebot (for #management)

    -translatebot fetch: fetch server secret
    -translatebot get: get translatebot secret key
    -translatebot set (value): set translatebot secret key
    """
    channel_name = ctx.channel.name
    result = ""

    if channel_name not in ("management"):
        result = ":warning: You don't have the permission to access this command."
        await ctx.send(result)
        return

    if args[0] not in ("fetch", "get", "set"):
        result = ":warning: Invalid command. Check -help translatebot for more information."
        await ctx.send(result)
        return

    if args[0] == "fetch":
        res = translate.get_secret().strip()
        result = f":white_check_mark: **Server Secret Key:** `{res}`"

    if args[0] == "get":
        result = f":white_check_mark: **Current Secret Key:** `{bot.curr_translate_secret}`"

    if args[0] == "set":
        bot.curr_translate_secret = args[1].strip()
        result = ":white_check_mark: Set Successful!"

    await ctx.send(result)


if __name__ == "__main__":
    print("Logging in..")
    bot.run(DISCORD_TOKEN)
