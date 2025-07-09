import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UsernameNotOccupied
from config import API_ID, API_HASH, ERROR_MESSAGE, IS_FSUB, DB_CHANNEL
from database.database import db
from plugins.fsub import get_fsub
from plugins.strings import HELP_TXT

class batch_temp:
    IS_BATCH = {}

async def downstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as f:
            txt = f.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloading:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

async def upstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as f:
            txt = f.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploading:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as f:
        f.write(f"{current * 100 / total:.2f}%")

START_TXT = (
    "<b>\ud83d\udc4b Hi {}, I am Save Restricted Content Bot \ud83e\udd16</b>\n\n"
    "<blockquote>I can help you retrieve and forward restricted content from Telegram posts. Use /help</blockquote>"
)

BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Update', url='https://t.me/UnknownBotz'),
        InlineKeyboardButton('Support', url='https://t.me/UnknownBotzChat')
    ]
])

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if IS_FSUB and not await get_fsub(client, message):
        return
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    await message.reply(START_TXT.format(message.from_user.mention), reply_markup=BUTTONS)

@Client.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply(HELP_TXT)

@Client.on_message(filters.command("cancel"))
async def cancel_command(client, message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await message.reply("**Batch Successfully Cancelled.**")

@Client.on_message(filters.text & filters.private)
async def save_content(client, message):
    if "https://t.me/" not in message.text:
        return

    if not batch_temp.IS_BATCH.get(message.from_user.id, True):
        return await message.reply("**One Task Is Already Processing. Use /cancel to stop it.**")

    datas = message.text.split("/")
    temp = datas[-1].replace("?single", "").split("-")

    try:
        fromID = int(temp[0].strip())
        toID = int(temp[1].strip()) if len(temp) > 1 else fromID
    except:
        return await message.reply("**Invalid link. Please check.**")

    user_data = await db.get_session(message.from_user.id)
    if not user_data:
        return await message.reply("**Please /login first to use this feature.**")

    batch_temp.IS_BATCH[message.from_user.id] = False

    async with Client("saverestricted", session_string=user_data, api_id=API_ID, api_hash=API_HASH) as acc:
        for msgid in range(fromID, toID + 1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            chatid = None
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
            elif "https://t.me/b/" in message.text:
                chatid = datas[4]
            else:
                chatid = datas[3]

            try:
                msg = await acc.get_messages(chatid, msgid)
                if not msg:
                    continue

                smsg = await message.reply("**Downloading...**")
                status_file_down = f'{message.id}downstatus.txt'
                asyncio.create_task(downstatus(client, status_file_down, smsg, message.chat.id))

                file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])

                if os.path.exists(status_file_down):
                    os.remove(status_file_down)

                if not file:
                    await smsg.delete()
                    continue

                status_file_up = f'{message.id}upstatus.txt'
                asyncio.create_task(upstatus(client, status_file_up, smsg, message.chat.id))

                await client.send_cached_media(
                    message.chat.id,
                    file,
                    caption=msg.caption or "",
                    reply_to_message_id=message.id
                )

                await client.send_cached_media(DB_CHANNEL, file, caption=msg.caption or "")

                if os.path.exists(status_file_up):
                    os.remove(status_file_up)
                if os.path.exists(file):
                    os.remove(file)

                await smsg.delete()

            except UsernameNotOccupied:
                await message.reply("The username is not occupied.")
            except Exception as e:
                if ERROR_MESSAGE:
                    await message.reply(f"Error: {e}")
            await asyncio.sleep(3)

    batch_temp.IS_BATCH[message.from_user.id] = True


def get_message_type(msg: Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass

