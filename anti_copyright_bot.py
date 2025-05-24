import os
import re
import sys
import time
import datetime
import random
import asyncio
import traceback
from pytz import timezone
from pymongo import MongoClient
from pyrogram import filters, Client, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.raw.types import UpdateEditMessage, UpdateEditChannelMessage
from apscheduler.schedulers.background import BackgroundScheduler

API_ID = "22243185"
API_HASH = "39d926a67155f59b722db787a23893ac"
BOT_TOKEN = "8020578503:AAFYsRcemAy7hqNQYersbtEOp8Mv1PdEcUM"
MONGO_URL = "mongodb+srv://manoranjanhor43:somuxd@manoranjan.wsglmdq.mongodb.net/?retryWrites=true&w=majority&appName=Manoranjan"
DEVS = "6908972904"
BOT_USERNAME = "silent_copyright_bot"
LOGS_GROUP_ID = "-1002100433415"  # এখানে তোমার লগ গ্রুপের ID দিন

# MongoDB Connection (Fixed)
mongo = MongoClient(MONGO_URL, tls=True)
db = mongo['copyright_bot']
groups_collection = db['groups']
users_collection = db['users']

DELETE_MESSAGE = [
    "1 Hour complete, I'm doing my work...",
    "Its time to delete all medias!",
    "No one can Copyright until I'm alive 😤",
    "Hue hue, let's delete media...",
    "I'm here to delete medias 🙋",
    "😮‍🚨 Finally I delete medias",
    "Great work done by me 🥲",
    "All media cleared!",
    "hue hue medias deleted by me 😮‍🚨",
    "medias....",
    "it's hard to delete all medias 🙄",
]

BLACKLIST_WORDS = ["mc","madarchod","randi","sex","xxx","gand","lund","land","bc","bhenchod","chut","lawda","gandu","spam","fuck","shit"]

DISABLE_CHATS = []
MEDIA_GROUPS = []
GROUP_MEDIAS = {}

bot = Client('bot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def add_user(user_id):
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})

def add_group(group_id):
    if not groups_collection.find_one({"group_id": group_id}):
        groups_collection.insert_one({"group_id": group_id})

async def send_log(text):
    try:
        await bot.send_message(LOGS_GROUP_ID, text)
    except Exception:
        pass

@bot.on_message(filters.command(["ping", "speed"]))
async def ping(_, e: Message):
    start = datetime.datetime.now()
    add_user(e.from_user.id)
    photo_url = "https://graph.org/file/b9300e15bf584bdff00a7-60231a72dc27cb029d.jpg"
    btn = [[
        InlineKeyboardButton("➕ Add Me", url=f"http://t.me/{BOT_USERNAME}?startgroup=true"),
        InlineKeyboardButton("❌ Close", callback_data="close")
    ]]
    rep = await e.reply_photo(
        photo=photo_url,
        caption="Checking Ping...",
        reply_markup=InlineKeyboardMarkup(btn)
    )
    end = datetime.datetime.now()
    ms = (end-start).microseconds / 1000
    await rep.edit_caption(f"🤖 PONG: `{ms}`ms", reply_markup=InlineKeyboardMarkup(btn))

@bot.on_message(filters.command(["help", "start"]))
async def start_message(_, message: Message):
    add_user(message.from_user.id)
    photo_url = "https://graph.org/file/bba38ef4b40c6860f52f5-72adfc3f156cb27ee7.jpg"
    btn = [[
        InlineKeyboardButton("+ Add me in group +", url=f"http://t.me/{BOT_USERNAME}?startgroup=true")
    ]]
    await message.reply_photo(
        photo=photo_url,
        caption=f"Hello {message.from_user.mention}, I'm Anti - CopyRight Bot!\n\n"
                "📌 I can save your groups from Copyrights.\n\n"
                "⚙️ What I do?\nI will delete all medias in your group every 1 hour.\n\n"
                "✅ Just add me in your group and make me admin with delete permission!",
        reply_markup=InlineKeyboardMarkup(btn)
    )
    # Log bot started by user
    log_text = (
        f"Bot started by new user\n\n"
        f"Name: {message.from_user.mention}\n"
        f"Username: @{message.from_user.username if message.from_user.username else 'No Username'}\n"
        f"UserID: `{message.from_user.id}`"
    )
    await send_log(log_text)

@bot.on_message(filters.user(DEVS) & filters.command(["restart", "reboot"]))
async def restart_(_, e: Message):
    await e.reply("Restarting.....")
    try:
        await bot.stop()
    except Exception:
        pass
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.user(DEVS) & filters.command(["stat", "stats"]))
async def status(_, message: Message):
    wait = await message.reply("Fetching.....")
    stats = (
        "📊 Here is total stats of me!\n\n"
        f"➤ Total Groups: {groups_collection.count_documents({})}\n"
        f"➤ Total Users: {users_collection.count_documents({})}\n"
        f"➤ Disabled Chats: {len(DISABLE_CHATS)}\n"
        f"➤ Media Active Chats: {len(MEDIA_GROUPS)}\n"
    )
    await wait.edit_text(stats)

@bot.on_message(filters.command(["anticopyright", "copyright"]))
async def enable_disable(bot: bot, message: Message):
    chat = message.chat
    if chat.id == message.from_user.id:
        await message.reply("Use this command in a group!")
        return
    add_group(chat.id)
    txt = ' '.join(message.command[1:])
    member = await bot.get_chat_member(chat.id, message.from_user.id)
    if re.search("on|yes|enable", txt, re.IGNORECASE):
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or message.from_user.id in DEVS:
            if chat.id in DISABLE_CHATS:
                DISABLE_CHATS.remove(chat.id)
                await message.reply(f"✅ Enabled anti-copyright for {chat.title}!")
            else:
                await message.reply("Already enabled!")
    elif re.search("off|no|disable", txt, re.IGNORECASE):
        if member.status == ChatMemberStatus.OWNER or message.from_user.id in DEVS:
            if chat.id not in DISABLE_CHATS:
                DISABLE_CHATS.append(chat.id)
                await message.reply(f"❌ Disabled anti-copyright for {chat.title}!")
            else:
                await message.reply("Already disabled!")
    else:
        status = "enabled" if chat.id not in DISABLE_CHATS else "disabled"
        await message.reply(f"Current status: `{status}`\nUse `/anticopyright enable` or `/anticopyright disable`")

@bot.on_message(filters.group)
async def watcher(_, message: Message):
    chat = message.chat
    if chat.id in DISABLE_CHATS:
        return
    add_group(chat.id)
    if message.from_user:
        add_user(message.from_user.id)
    text_lower = message.text.lower() if message.text else ""
    for word in BLACKLIST_WORDS:
        if word in text_lower:
            try:
                await message.delete()
                warn = await message.reply_text(f"🚫 The word '{word}' is not allowed here!")
                await asyncio.sleep(5)
                await warn.delete()
            except:
                pass
            return
    if message.video or message.photo or message.animation or message.document:
        GROUP_MEDIAS.setdefault(chat.id, []).append(message.id)
        if chat.id not in MEDIA_GROUPS:
            MEDIA_GROUPS.append(chat.id)

@bot.on_raw_update(group=-1)
async def edited(_, update, __, ___):
    try:
        if isinstance(update, (UpdateEditMessage, UpdateEditChannelMessage)):
            e = update.message
            if hasattr(e, 'from_id') and hasattr(e.from_id, 'user_id'):
                user_id = e.from_id.user_id
                if user_id in DEVS:
                    return
            chat_id = f"-100{e.peer_id.channel_id}"
            await _.delete_messages(int(chat_id), [e.id])
    except Exception:
        traceback.print_exc()

@bot.on_chat_member_updated()
async def on_bot_added(client, update):
    if update.new_chat_member.user.is_bot and update.new_chat_member.user.id == client.me.id:
        chat = update.chat
        add_group(chat.id)
        text = (
            f"Bot added in new group\n\n"
            f"Name: {chat.title}\n"
            f"Username: @{chat.username if chat.username else 'No Username'}\n"
            f"Group ID: `{chat.id}`\n"
        )
        await send_log(text)

def AutoDelete():
    for chat_id in list(MEDIA_GROUPS):
        if chat_id in DISABLE_CHATS:
            continue
        messages = GROUP_MEDIAS.get(chat_id, [])
        try:
            bot.delete_messages(chat_id, messages)
            GROUP_MEDIAS[chat_id] = []
        except:
            pass

scheduler = BackgroundScheduler(timezone=timezone('Asia/Kolkata'))
scheduler.add_job(AutoDelete, "interval", hours=1)
scheduler.start()

def starter():
    print('Starting Bot...')
    if os.path.exists("bot.session"):
        os.remove("bot.session")
    bot.start()
    print('Bot Started ✓')
    idle()

if __name__ == "__main__":
    starter()