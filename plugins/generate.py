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
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        return 
    await db.set_session(message.from_user.id, session=None)  
    await message.reply("𝖫𝗈𝗀𝗈𝗎𝗍 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒")

from pyrogram_conversation import Conversation

@Client.on_message(filters.private & filters.command("login"))
async def main(bot: Client, message: Message):
    user_id = message.from_user.id
    user_data = await db.get_session(user_id)
    if user_data is not None:
        await message.reply("You're already logged in. Please /logout first.")
        return

    async with Conversation(bot, user_id) as conv:
        phone_msg = await conv.ask("📱 Send your phone number including the country code:\nExample: `+13124562345`", filters=filters.text)
        if phone_msg.text == "/cancel":
            return await phone_msg.reply("❌ Cancelled.")

        phone_number = phone_msg.text
        client = Client(":memory:", API_ID, API_HASH)
        await client.connect()
        await message.reply("📨 Sending OTP...")

        try:
            code = await client.send_code(phone_number)
            otp_msg = await conv.ask("🔑 Enter the OTP as shown (e.g., `1 2 3 4 5`):", filters=filters.text, timeout=300)
            if otp_msg.text == "/cancel":
                return await otp_msg.reply("❌ Cancelled.")
            otp_code = otp_msg.text.replace(" ", "")
            await client.sign_in(phone_number, code.phone_code_hash, otp_code)
        except PhoneNumberInvalid:
            return await message.reply("❌ Invalid phone number.")
        except PhoneCodeInvalid:
            return await message.reply("❌ Invalid OTP.")
        except PhoneCodeExpired:
            return await message.reply("⌛ OTP expired.")
        except SessionPasswordNeeded:
            pw_msg = await conv.ask("🔒 Two-step verification enabled. Enter your password:", filters=filters.text, timeout=300)
            if pw_msg.text == "/cancel":
                return await pw_msg.reply("❌ Cancelled.")
            try:
                await client.check_password(pw_msg.text)
            except PasswordHashInvalid:
                return await pw_msg.reply("❌ Invalid password.")

        # Save session
        session_string = await client.export_session_string()
        await client.disconnect()

        if len(session_string) < SESSION_STRING_SIZE:
            return await message.reply("⚠️ Invalid session string.")
        await db.set_session(user_id, session=session_string)
        return await message.reply("✅ Logged in successfully.")
