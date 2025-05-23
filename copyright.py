import os import re import sys import time import datetime import random import asyncio from pytz import timezone from pyrogram import filters, Client, idle from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton from pyrogram.enums import ChatMemberStatus, ChatType from pyrogram.raw.types import UpdateEditMessage, UpdateEditChannelMessage import traceback

from apscheduler.schedulers.background import BackgroundScheduler

API_ID = "22243185" API_HASH = "39d926a67155f59b722db787a23893ac" BOT_TOKEN = "8020578503:AAEPufV2GAM26SvKafJYIAQh4ARPaWRZNA0" DEVS = [6908972904] BOT_USERNAME = "silent_copyright_bot"

ALL_GROUPS = [] TOTAL_USERS = [] MEDIA_GROUPS = [] DISABLE_CHATS = [] GROUP_MEDIAS = {}

BLACKLIST_WORDS = ["mc","madarchod","randi","sex","xxx","gand","lund","land","bc","bhenchod","chut","lawda","gandu", "spam", "fuck", "shit"]

DELETE_MESSAGE = [ "1 Hour complete, I'm doing my work...", "Its time to delete all medias!", "No one can Copyright until I'm alive ", "Hue hue, let's delete media...", "I'm here to delete medias ", " Finally I delete medias", "Great work done by me ", "All media cleared!", "hue hue medias deleted by me ", "medias....", "it's hard to delete all medias ", ]

START_MESSAGE = """ Hello {}, I'm Anti - CopyRight Bot

> **I can save your groups from Copyrights **



Work: I'll Delete all medias of your group in every 1 hour

Process?: Simply add me in your group and promote as admin with delete messages right! """

BUTTON = [[InlineKeyboardButton("+ Add me in group +", url=f"http://t.me/{BOT_USERNAME}?startgroup=s&admin=delete_messages")]]

bot = Client('bot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def add_user(user_id): if user_id not in TOTAL_USERS: TOTAL_USERS.append(user_id)

@bot.on_message(filters.command(["ping", "speed"])) async def ping(_, e: Message): start = datetime.datetime.now() add_user(e.from_user.id) rep = await e.reply_text("Pong !!") end = datetime.datetime.now() ms = (end-start).microseconds / 1000 await rep.edit_text(f" PONG: {ms}ᴍs")

@bot.on_message(filters.command(["help", "start"])) async def start_message(_, message: Message): add_user(message.from_user.id) await message.reply(START_MESSAGE.format(message.from_user.mention), reply_markup=InlineKeyboardMarkup(BUTTON))

@bot.on_message(filters.user(DEVS) & filters.command(["restart", "reboot"])) async def restart_(_, e: Message): await e.reply("Restarting.....") try: await bot.stop() except Exception: pass args = [sys.executable, "copyright.py"] os.execl(sys.executable, *args) quit()

@bot.on_message(filters.user(DEVS) & filters.command(["stat", "stats"])) async def status(_, message: Message): wait = await message.reply("Fetching.....") stats = "Here is total stats of me! \n\n" stats += f"Total Chats: {len(ALL_GROUPS)} \n" stats += f"Total users: {len(TOTAL_USERS)} \n" stats += f"Disabled chats: {len(DISABLE_CHATS)} \n" stats += f"Total Media active chats: {len(MEDIA_GROUPS)} \n\n" await wait.edit_text(stats)

@bot.on_message(filters.command(["anticopyright", "copyright"])) async def enable_disable(bot: bot, message: Message): chat = message.chat if chat.id == message.from_user.id: await message.reply("Use this command in group!") return txt = ' '.join(message.command[1:]) if txt: member = await bot.get_chat_member(chat.id, message.from_user.id) if re.search("on|yes|enable", txt.lower()): if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or member.user.id in DEVS: if chat.id in DISABLE_CHATS: await message.reply(f"Enabled anti-copyright! for {chat.title}") DISABLE_CHATS.remove(chat.id) return await message.reply("Already enabled!") elif re.search("no|off|disable", txt.lower()): if member.status == ChatMemberStatus.OWNER or member.user.id in DEVS: if chat.id in DISABLE_CHATS: await message.reply("Already disabled!") return DISABLE_CHATS.append(chat.id) if chat.id in MEDIA_GROUPS: MEDIA_GROUPS.remove(chat.id) await message.reply(f"Disable Anti-CopyRight for {chat.title}!") else: await message.reply("Only chat Owner can disable anti-copyright!") return else: if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or member.user.id in DEVS: if chat.id in DISABLE_CHATS: await message.reply("Anti-Copyright is disable for this chat! \n\ntype /anticopyright enable to enable Anti-CopyRight") else: await message.reply("Anti-Copyright is enable for this chat! \n\ntype /anticopyright disable to disable Anti-CopyRight") else: if chat.id in DISABLE_CHATS: await message.reply("Anti-Copyright is disable for this chat! \n\ntype /anticopyright enable to enable Anti-CopyRight") else: await message.reply("Anti-Copyright is enable for this chat! \n\ntype /anticopyright disable to disable Anti-CopyRight")

@bot.on_message(filters.all & filters.group) async def watcher(_, message: Message): chat = message.chat text_lower = message.text.lower() if message.text else ""

if chat.id not in ALL_GROUPS: ALL_GROUPS.append(chat.id)

if chat.id in DISABLE_CHATS: return

if chat.id not in MEDIA_GROUPS: MEDIA_GROUPS.append(chat.id)

for word in BLACKLIST_WORDS: if word in text_lower: try: await message.delete() warn_msg = await message.reply_text(f"\u26d4 The word '{word}' is not allowed in this group!") await asyncio.sleep(5) await warn_msg.delete() except Exception: pass return

if message.video or message.photo or message.animation or message.document: GROUP_MEDIAS.setdefault(chat.id, []).append(message.id)

@bot.on_raw_update(group=-1) async def better(client, update, _, __): if isinstance(update, (UpdateEditMessage, UpdateEditChannelMessage)): try: user_id = update.message.from_id.user_id if user_id in DEVS: return chat_id = f"-100{update.message.peer_id.channel_id}" await client.delete_messages(chat_id=chat_id, message_ids=update.message.id) user = await client.get_users(user_id) await client.send_message(chat_id, f"{user.mention} just edited a message, and I deleted it .") except Exception: print("Error occurred:", traceback.format_exc())

def AutoDelete(): for i in list(MEDIA_GROUPS): if i in DISABLE_CHATS: continue message_list = GROUP_MEDIAS.get(i, []) try: bot.send_message(i, random.choice(DELETE_MESSAGE)) bot.delete_messages(i, message_list, revoke=True) GROUP_MEDIAS[i].clear() bot.send_message(i, text="Deleted All Media's") except Exception: pass print("Cleaned all medias ✓")

scheduler = BackgroundScheduler(timezone=timezone('Asia/Kolkata')) scheduler.add_job(AutoDelete, "interval", seconds=3600) scheduler.start()

def starter(): print('Starting Bot...') bot.start() print('Bot Started ✓') idle()

if name == "main": starter()

