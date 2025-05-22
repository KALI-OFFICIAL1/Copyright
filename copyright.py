from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import re
import datetime
import os

API_ID = 12345678  # Replace with your API ID
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
LOGS_CHAT = -1001234567890  # Replace with your logs group/chat id
OWNER_USERNAME = "@moh_maya_official"
SUPPORT_USERNAME = "@frozenTools"

app = Client("group_security_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

abuse_words = [
    "madarchod", "bhenchodd", "lund", "chut", "gaand", "bsdk", "bahanchod",
    "ncert", "allen", "porn", "xxx", "sex", "NCERT", "XII", "page", "Ans",
    "meiotic", "divisions", "System.in", "Scanner", "void", "nextInt"
]

link_pattern = re.compile(r"(http[s]?://|t\.me|www\.)")

@app.on_message(filters.new_chat_members)
async def new_group_handler(client, message):
    for member in message.new_chat_members:
        if member.id == (await app.get_me()).id:
            chat = message.chat
            await app.send_message(
                LOGS_CHAT,
                f"Bot added in new group:\nGroup: {chat.title}\nGroup ID: {chat.id}\nUsername: @{chat.username or 'N/A'}\nBy: {message.from_user.mention} ({message.from_user.id})"
            )

@app.on_message(filters.private & filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    await message.reply_photo(
        photo="https://envs.sh/52H.jpg",
        caption=("🤖 𝖦𝗋𝗈𝗎𝗉 𝖲𝖾𝖼𝗎𝗋𝗂𝗍𝗒 𝖱𝗈𝖻𝗈𝗍 🛡️\n"
                 "𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝖦𝗋𝗈𝗎𝗉𝖲𝖾𝖼𝗎𝗋𝗂𝗍𝗒𝖱𝗈𝖻𝗈𝗍, 𝗒𝗈𝗎𝗋 𝗏𝗂𝗀𝗂𝗅𝖺𝗇𝗍 𝗀𝗎𝖺𝗋𝖽𝗂𝖺𝗇 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆 𝗌𝗉𝖺𝖼𝖾!\n"
                 "𝖮𝗎𝗋 𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗂𝗌 𝗍𝗈 𝖾𝗇𝗌𝗎𝗋𝖾 𝖺 𝗌𝖾𝖼𝗎𝗋𝖾 𝖺𝗇𝖽 𝗉𝗅𝖾𝖺𝗌𝖺𝗇𝗍 𝖾𝗇𝗏𝗂𝗋𝗈𝗇𝗆𝖾𝗇𝗍 𝖿𝗈𝗋 𝖾𝗏𝖾𝗋𝗒𝗈𝗇𝖾."),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Owner", url=f"https://t.me/{OWNER_USERNAME[1:]}"),
             InlineKeyboardButton("Support", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")],
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{(await app.get_me()).username}?startgroup=true")]
        ])
    )
    await app.send_message(
        LOGS_CHAT,
        f"Bot started by new user:\nName: {user.first_name}\nUsername: @{user.username}\nID: {user.id}"
    )

@app.on_message(filters.command("ping"))
async def ping_handler(client, message):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await message.reply_photo(
        photo="https://envs.sh/r-v.jpg",
        caption=f"🏓 Pong!\nTime: {now}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])
    )

@app.on_callback_query(filters.regex("close"))
async def close_ping(client, callback_query):
    await callback_query.message.delete()

@app.on_message(filters.command("broadcast") & filters.user(OWNER_USERNAME))
async def broadcast_handler(client, message):
    if len(message.text.split(" ", 1)) < 2:
        return await message.reply("Usage: `/broadcast Your Message Here`", quote=True)
    text = message.text.split(" ", 1)[1]
    count = 0
    async for user in app.get_users():
        try:
            await app.send_message(user.id, text)
            count += 1
        except:
            pass
    await message.reply(f"Broadcast sent to {count} users.")

@app.on_message(filters.group)
async def group_guard(client, message: Message):
    text = message.text or ""

    # 1. Delete long messages
    if len(text) > 200:
        return await message.delete()

    # 2. Delete PDFs
    if message.document and message.document.mime_type == "application/pdf":
        return await message.delete()

    # 3. Delete edited messages
    if message.edit_date:
        return await message.delete()

    # 4. Delete links
    if link_pattern.search(text.lower()):
        return await message.delete()

    # 5. Mute users whose bio contains link
    try:
        bio = (await client.get_users(message.from_user.id)).bio or ""
        if link_pattern.search(bio.lower()):
            await message.chat.restrict_member(message.from_user.id, permissions={})
            await message.reply(f"{message.from_user.mention} muted due to link in bio.")
    except:
        pass

    # 6. Delete abusive messages
    if any(word.lower() in text.lower() for word in abuse_words):
        return await message.delete()

app.run()