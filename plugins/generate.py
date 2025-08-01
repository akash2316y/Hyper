import asyncio
import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from database.database import db

SESSION_STRING_SIZE = 351

# ✅ Custom ask() function
async def ask(client: Client, user_id: int, text: str, timeout: int = 300) -> Message:
    await client.send_message(user_id, text)

    future = asyncio.get_event_loop().create_future()

    async def response_handler(_, msg: Message):
        if msg.from_user.id == user_id:
            if not future.done():
                future.set_result(msg)
            client.remove_handler(response_handler, group=1)

    client.add_handler(response_handler, group=1)

    try:
        return await asyncio.wait_for(future, timeout)
    except asyncio.TimeoutError:
        await client.send_message(user_id, "❌ Timeout. Please try again later.")
        raise

# ✅ /logout command
@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        return 
    await db.set_session(message.from_user.id, session=None)  
    await message.reply("**Logout Successfully** ♦")

# ✅ /login command
@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**You are already logged in. First /logout your old session, then do login again.**")
        return 

    user_id = message.from_user.id

    try:
        # Ask for phone number
        phone_number_msg = await ask(bot, user_id, "<b>Please send your phone number which includes country code</b>\n<b>Example:</b> <code>+13124562345, +9171828181889</code>")
        if phone_number_msg.text == '/cancel':
            return await phone_number_msg.reply('<b>Process cancelled!</b>')

        phone_number = phone_number_msg.text

        # Start temp client
        client = Client(":memory:", api_id=API_ID, api_hash=API_HASH)
        await client.connect()

        await phone_number_msg.reply("Sending OTP...")

        try:
            code = await client.send_code(phone_number)

            # Ask for OTP
            phone_code_msg = await ask(bot, user_id,
                "Please check your official Telegram app for OTP.\n\n"
                "If OTP is `12345`, **send it as** `1 2 3 4 5`\n\n"
                "**Enter /cancel to cancel the process.**", timeout=600)

        except PhoneNumberInvalid:
            await phone_number_msg.reply('❌ `PHONE_NUMBER` is invalid.')
            await client.disconnect()
            return

        if phone_code_msg.text == '/cancel':
            await client.disconnect()
            return await phone_code_msg.reply('<b>Process cancelled!</b>')

        try:
            phone_code = phone_code_msg.text.replace(" ", "")
            await client.sign_in(phone_number, code.phone_code_hash, phone_code)

        except PhoneCodeInvalid:
            await client.disconnect()
            return await phone_code_msg.reply('❌ OTP is invalid.')
        except PhoneCodeExpired:
            await client.disconnect()
            return await phone_code_msg.reply('⌛ OTP is expired.')
        except SessionPasswordNeeded:
            # Ask for 2FA password
            two_step_msg = await ask(bot, user_id,
                '**Your account has two-step verification enabled.**\n'
                '**Please send your password.**\n\n'
                'Enter /cancel to cancel.', timeout=300)

            if two_step_msg.text == '/cancel':
                await client.disconnect()
                return await two_step_msg.reply('<b>Process cancelled!</b>')

            try:
                await client.check_password(two_step_msg.text)
            except PasswordHashInvalid:
                await client.disconnect()
                return await two_step_msg.reply('❌ Invalid password.')

        # Save session
        string_session = await client.export_session_string()
        await client.disconnect()

        if len(string_session) < SESSION_STRING_SIZE:
            return await message.reply('<b>Invalid session string</b>')

        # Store session in DB
        user_data = await db.get_session(user_id)
        if user_data is None:
            uclient = Client(":memory:", session_string=string_session, api_id=API_ID, api_hash=API_HASH)
            await uclient.connect()
            await db.set_session(user_id, session=string_session)

        await bot.send_message(user_id,
            "<b>✅ Account login successful.</b>\n\n"
            "If you get any AUTH KEY related error, please /logout and then /login again.")

    except Exception as e:
        error_text = f"<b>⚠️ ERROR IN LOGIN:</b> <code>{str(e)}</code>"
        await bot.send_message(user_id, error_text)
