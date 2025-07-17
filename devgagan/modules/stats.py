# ---------------------------------------------------
# File Name: stats.py
# Description: A Pyrogram bot for downloading files from Telegram channels or groups 
#              and uploading them back to Telegram.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# ---------------------------------------------------


import os
import time
import sys
import motor
from devgagan import app
from pyrogram import filters
from config import OWNER_ID
from devgagan.core.mongo.users_db import get_users, add_user, get_user
from devgagan.core.mongo.plans_db import premium_users
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ChatType


@app.on_message(filters.command("id"))
async def id_command(client, message: Message):
    reply = message.reply_to_message

    user = reply.from_user if reply else message.from_user
    user_id = user.id if user else "N/A"
    chat_id = message.chat.id
    msg_id = message.id
    reply_id = reply.message_id if reply else "N/A"

    text = (
        f"👤 User ID: `{user_id}`\n"
        f"💬 Chat ID: `{chat_id}`\n"
        f"📎 Message ID: `{msg_id}`\n"
        f"🔁 Reply to Msg ID: `{reply_id}`"
    )

    await message.reply_text(text, quote=True)


start_time = time.time()

@app.on_message(group=10)
async def chat_watcher_func(_, message):
    try:
        if message.from_user:
            us_in_db = await get_user(message.from_user.id)
            if not us_in_db:
                await add_user(message.from_user.id)
    except:
        pass



def time_formatter():
    minutes, seconds = divmod(int(time.time() - start_time), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + "w:") if weeks else "")
        + ((str(days) + "d:") if days else "")
        + ((str(hours) + "h:") if hours else "")
        + ((str(minutes) + "m:") if minutes else "")
        + ((str(seconds) + "s") if seconds else "")
    )
    if tmp != "":
        if tmp.endswith(":"):
            return tmp[:-1]
        else:
            return tmp
    else:
        return "0 s"


@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message):
    start = time.time()
    users = len(await get_users())
    premium = await premium_users()
    ping = round((time.time() - start) * 1000)
    await message.reply_text(f"""
**Stats of** {(await client.get_me()).mention} :

🏓 **Ping Pong**: {ping}ms

📊 **Total Users** : `{users}`
📈 **Premium Users** : `{len(premium)}`
⚙️ **Bot Uptime** : `{time_formatter()}`
    
🎨 **Python Version**: `{sys.version.split()[0]}`
📑 **Mongo Version**: `{motor.version}`
""")

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery
)

# /getusers command — OWNER only, private chat
@app.on_message(filters.command("getusers") & filters.user(OWNER_ID) & filters.private)
async def getusers_paginated(client, message: Message):
    users = await get_users()
    if not users:
        return await message.reply("🚫 No users found in the database.")
    await show_users_page(client, message.chat.id, users, page=0)


# Pagination callback handler
@app.on_callback_query(filters.regex(r"^users_page_(\d+)$") & filters.user(OWNER_ID))
async def paginate_users_callback(client, query: CallbackQuery):
    page = int(query.matches[0].group(1))
    users = await get_users()
    await show_users_page(client, query.message.chat.id, users, page, query)


# Helper: show paginated user list
async def show_users_page(client, chat_id, users, page=0, query=None):
    users_per_page = 20
    start = page * users_per_page
    end = start + users_per_page
    user_chunk = users[start:end]

    lines = []
    for uid in user_chunk:
        try:
            user = await client.get_users(uid)
            name = f"{user.first_name or ''} {user.last_name or ''}".strip() or str(uid)
            name = name.replace('[', '').replace(']', '')  # Avoid markdown conflicts
            mention = f"[`{name}`](tg://user?id={uid})"
        except:
            mention = f"[`{uid}`](tg://user?id={uid})"
        lines.append(f"• {mention} — `{uid}`")

    text = f"👥 **Users {start+1} - {min(end, len(users))} of {len(users)}**:\n\n" + "\n".join(lines)

    # Pagination buttons
    buttons = []
    if start > 0:
        buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"users_page_{page - 1}"))
    if end < len(users):
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"users_page_{page + 1}"))

    markup = InlineKeyboardMarkup([buttons]) if buttons else None

    if query:
        await query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
        await query.answer()
    else:
        await client.send_message(chat_id, text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
