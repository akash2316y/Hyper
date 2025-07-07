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

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_id = message.from_user.id
    session_string = await db.get_session(user_id)
    if not session_string:
        return await message.reply("❌ **You're not logged in.**")

    try:
        temp_client = Client("anon", session_string=session_string, api_id=API_ID, api_hash=API_HASH)
        await temp_client.connect()
        await temp_client.log_out()
        await temp_client.disconnect()
    except:
        pass

    await db.set_session(user_id, session=None)
    await message.reply("✅ **Logout successful!**")


@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_data = await db.get_session(message.from_user.id)
    if user_data:
        await message.reply("**You are already logged in. Use /logout first.**")
        return

    user_id = message.from_user.id
    phone_number_msg = await bot.ask(user_id, "<b>Send phone number with country code</b>", timeout=300)
    if phone_number_msg.text == '/cancel':
        return await message.reply('<b>Process cancelled!</b>')

    phone_number = phone_number_msg.text
    client = Client("anon", API_ID, API_HASH)  # 🔑 Give a session name for persistence
    await client.connect()

    try:
        code = await client.send_code(phone_number)
        otp_msg = await bot.ask(user_id, "<b>Enter OTP like 1 2 3 4 5</b>", timeout=600)
        if otp_msg.text == '/cancel':
            await client.disconnect()
            return await message.reply('<b>Process cancelled!</b>')

        otp = otp_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, otp)

    except PhoneNumberInvalid:
        await client.disconnect()
        return await message.reply("**Invalid phone number.**")
    except PhoneCodeInvalid:
        await client.disconnect()
        return await message.reply("**Invalid OTP.**")
    except PhoneCodeExpired:
        await client.disconnect()
        return await message.reply("**OTP expired. Try again.**")
    except SessionPasswordNeeded:
        pw_msg = await bot.ask(user_id, "<b>2FA Password?</b>", timeout=300)
        if pw_msg.text == '/cancel':
            await client.disconnect()
            return await message.reply('<b>Process cancelled!</b>')
        try:
            await client.check_password(pw_msg.text)
        except PasswordHashInvalid:
            await client.disconnect()
            return await message.reply("**Wrong password.**")

    string_session = await client.export_session_string()
    await client.disconnect()

    await db.set_session(user_id, session=string_session)
    await message.reply("✅ **Logged in successfully!**\n\nIf you face any issues, use /logout and try /login again.")
