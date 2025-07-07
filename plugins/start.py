import os, time
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated,
    UserAlreadyParticipant,
    InviteHashExpired,
    UsernameNotOccupied
)
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import API_ID, API_HASH, ERROR_MESSAGE, IS_FSUB, DB_CHANNEL
from database.database import db
from plugins.strings import HELP_TXT
from plugins.fsub import get_fsub

class batch_temp(object):
    IS_BATCH = {}


async def downstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(1)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, txt)
            await asyncio.sleep(1)
        except:
            await asyncio.sleep(1)


async def upstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(1)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, txt)
            await asyncio.sleep(1)
        except:
            await asyncio.sleep(1)


def human_readable_size(size):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PiB"

#-------------------------x---------------------x-------------

def progress(current, total, message, type):
    now = time.time()
    percentage = current * 100 / total
    bar_length = 10
    filled_length = int(bar_length * percentage // 100)
    bar = '▪️' * filled_length + '▫️' * (bar_length - filled_length)

    downloaded = human_readable_size(current)
    total_size = human_readable_size(total)

    if not hasattr(message, f"{type}_start"):
        setattr(message, f"{type}_start", now)

    elapsed_time = max(now - getattr(message, f"{type}_start", now), 0.1)
    speed = current / elapsed_time
    eta = (total - current) / speed if speed > 0 else 0

    mins, secs = divmod(int(eta), 60)
    eta_str = f"{mins}m, {secs}s"

    display = (
        f"**{'📥 Downloading...' if type == 'down' else '📤 Uploading...'}**\n\n"
        f"**[{bar}]**\n"
        f"Progress: `{percentage:.2f}%`\n"
        f"Size: `{downloaded} of {total_size}`\n"
        f"Speed: `{human_readable_size(speed)}/s`\n"
        f"ETA: `{eta_str}`"
    )

    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(display)

#-------------------------x---------------------x-------------

START_TXT = (
    "<b>👋 𝖧𝗂 {}, 𝖨 𝖺𝗆 𝖲𝖺𝗏𝖾 𝖱𝖾𝗌𝗍𝗋𝗂𝖼𝗍𝖾𝖽 𝖢𝗈𝗇𝗍𝖾𝗇𝗍 𝖡𝗈𝗍 🤖</b>\n\n"
    "<blockquote>𝖨 𝖼𝖺𝗇 𝗁𝖾𝗅𝗉 𝗒𝗈𝗎 𝗋𝖾𝗍𝗋𝗂𝖾𝗏𝖾 𝖺𝗇𝖽 𝖿𝗈𝗋𝗐𝖺𝗋𝖽 𝗋𝖾𝗌𝗍𝗋𝗂𝖼𝗍𝖾𝖽 𝖼𝗈𝗇𝗍𝖾𝗇𝗍 𝖿𝗋𝗈𝗆 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆 𝗉𝗈𝗌𝗍𝗌.</blockquote>"
)


def get_start_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton('𝖴𝗉𝖽𝖺𝗍𝖾', url='https://t.me/UnknownBotz'),
            InlineKeyboardButton('𝖲𝗎𝗉𝗉𝗈𝗋𝗍', url='https://t.me/UnknownBotzChat')
        ],
        [
            InlineKeyboardButton('𝖧𝖾𝗅𝗉', callback_data='help_callback'),
            InlineKeyboardButton('𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋', url='tg://openmessage?user_id=6165669080')
        ]
    ])


@Client.on_message(filters.command(["start"]) & filters.private)
async def send_start(client: Client, message: Message):
    if IS_FSUB:
        if not await get_fsub(client, message):
            return

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    await client.send_message(
        chat_id=message.chat.id,
        text=START_TXT.format(message.from_user.mention),
        reply_markup=get_start_buttons(),
        reply_to_message_id=message.id
    )


@Client.on_callback_query()
async def callback_query_handler(client: Client, callback_query: CallbackQuery):
    if callback_query.data == 'help_callback':
        await callback_query.answer()
        help_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("𝖡𝖺𝖼𝗄", callback_data="back_callback"),
                InlineKeyboardButton("𝖢𝗅𝗈𝗌𝖾", callback_data="close_callback")
            ]
        ])
        await callback_query.edit_message_text(
            text=HELP_TXT,
            reply_markup=help_buttons
        )

    elif callback_query.data == 'back_callback':
        await callback_query.answer()
        await callback_query.edit_message_text(
            text=START_TXT.format(callback_query.from_user.mention),
            reply_markup=get_start_buttons()
        )

    elif callback_query.data == 'close_callback':
        await callback_query.answer()
        await callback_query.message.delete()


@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(chat_id=message.chat.id, text="𝖡𝖺𝗍𝖼𝗁 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽.‼️")


@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
        batch_temp.IS_BATCH[message.from_user.id] = False
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                batch_temp.IS_BATCH[message.from_user.id] = True
                return
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
            except:
                batch_temp.IS_BATCH[message.from_user.id] = True
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
            
            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try:    
                        await handle_private(client, acc, message, username, msgid)               
                    except Exception as e:
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(3)
        batch_temp.IS_BATCH[message.from_user.id] = True


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
            
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
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


    buttons = []
    if msg.reply_markup and msg.reply_markup.inline_keyboard:
        for row in msg.reply_markup.inline_keyboard:
            for button in row:
                if button.url:
                    buttons.append([InlineKeyboardButton(button.text, url=button.url)])

    try:
        send_func = getattr(client, f"send_{msg_type}", None)   # 👉 Properly indented
        if send_func:
            try:
                await send_func(
                    DB_CHANNEL,
                    file,
                    caption=caption_db,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
                )
            except Exception as db_err:
                print(f"Error sending to DB_CHANNEL: {db_err}")

        await smsg.delete()

    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(chat, f"❌ Error: {e}", reply_to_message_id=message.id)
        await smsg.delete()
