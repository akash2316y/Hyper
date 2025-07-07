from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import IS_FSUB
from pyrogram.types import CallbackQuery
from .fsub import get_fsub
from database.db import db
from .strings import HELP_TXT

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
    print("✅ Start command triggered")
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
    if "https://t.me/" not in message.text:
        return

    if batch_temp.IS_BATCH.get(message.from_user.id) == False:
        return await message.reply_text("𝖳𝖺𝗌𝗄 𝗂𝗌 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝗉𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀. \n𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗌𝗍𝗈𝗉.")

    urls = [x.strip() for x in message.text.split("\n") if x.startswith("https://t.me/")]

    for link in urls:
        datas = link.split("/")
        temp = datas[-1].replace("?single", "").split("-")

        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        batch_temp.IS_BATCH[message.from_user.id] = False

        for msgid in range(fromID, toID + 1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("𝖯𝗅𝖾𝖺𝗌𝖾 /login 𝗍𝗈 𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝖾.")
                batch_temp.IS_BATCH[message.from_user.id] = True
                return

            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
            except:
                batch_temp.IS_BATCH[message.from_user.id] = True
                return await message.reply("𝖲𝖾𝗌𝗌𝗂𝗈𝗇 𝖾𝗑𝗉𝗂𝗋𝖾𝖽. \n𝖴𝗌𝖾 /logout 𝖺𝗇𝖽 /login 𝖺𝗀𝖺𝗂𝗇.")

            if "https://t.me/c/" in link:
                chatid = int("-100" + datas[4])
            else:
                chatid = datas[3]

            try:
                await handle_private(client, acc, message, chatid, msgid)
            except Exception as e:
                if ERROR_MESSAGE:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            await asyncio.sleep(1)

        batch_temp.IS_BATCH[message.from_user.id] = True

#-------------------------x---------------------x-------------

async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg = await acc.get_messages(chatid, msgid)
    if not msg or msg.empty:
        return

    msg_type = None
    for attr in ["document", "video", "animation", "sticker", "voice", "audio", "photo", "text"]:
        if getattr(msg, attr, None):
            msg_type = attr
            break

    if not msg_type:
        return

    chat = message.chat.id
    user_tag = f"From: [{message.from_user.first_name}](tg://user?id={message.from_user.id})"

    # Start Download message
    smsg = await client.send_message(chat, '**📥 Downloading...**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))

    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(chat, f"❌ Error: {e}", reply_to_message_id=message.id)
        await smsg.delete()
        return

    # Show Upload message
    await smsg.edit_text('**📤 Uploading...**')
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    # Get Caption and File Name
    caption_user = msg.caption or msg.text or ""
    file_name = None

    if hasattr(msg, "document") and msg.document:
        file_name = msg.document.file_name
    elif hasattr(msg, "video") and msg.video:
        file_name = msg.video.file_name
    elif hasattr(msg, "audio") and msg.audio:
        file_name = msg.audio.file_name
    elif hasattr(msg, "animation") and msg.animation:
        file_name = msg.animation.file_name
    elif hasattr(msg, "sticker") and msg.sticker:
        file_name = "Sticker.webp"
    elif hasattr(msg, "photo") and msg.photo:
        file_name = "Image.jpg"
    elif hasattr(msg, "voice") and msg.voice:
        file_name = "Voice.ogg"

    display_file_name = f"**📄 {file_name}**\n\n" if file_name else ""
    caption_display = display_file_name + caption_user
    caption_db = display_file_name + caption_user + f"\n\n{user_tag}"

    buttons = []
    if msg.reply_markup and msg.reply_markup.inline_keyboard:
        for row in msg.reply_markup.inline_keyboard:
            for button in row:
                if button.url:
                    buttons.append([InlineKeyboardButton(button.text, url=button.url)])

    send_args = dict(
        caption=caption_display,
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.MARKDOWN,
        progress=progress,
        progress_args=[message, "up"]
    )

    try:
        send_func = getattr(client, f"send_{msg_type}", None)
        if send_func:
            # ✅ Send to User Chat
            await send_func(chat, file, **send_args, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)

            await smsg.delete()

            # ✅ Send to DB_CHANNEL
            try:
                await send_func(DB_CHANNEL, file, caption=caption_db, parse_mode=enums.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)
            except Exception as db_err:
                print(f"Error sending to DB_CHANNEL: {db_err}")

            # ✅ Send to User's Personal Channel (if set)
            user_channel = await db.get_channel(message.from_user.id)
            if user_channel:
                try:
                    await send_func(int(user_channel), file, caption=caption_db, parse_mode=enums.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)
                except Exception as e:
                    print(f"❌ Failed to send to user's channel: {e}")

    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(chat, f"❌ Error: {e}", reply_to_message_id=message.id)
        await smsg.delete()

