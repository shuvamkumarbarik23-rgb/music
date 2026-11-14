
import asyncio
import logging

from pyrogram import Client, filters, idle
from pyrogram.types import Message

from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    STRING_SESSION,
    OWNER_ID,
    STREAM_URL
)



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("sukuna-x-music")

# Telegram bot
bot = Client(
    "sukuna_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Assistant account for voice chat
assistant = Client(
    "sukuna_assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

calls = PyTgCalls(assistant)

playing_chats = set()


def is_owner(message: Message):
    return (
        message.from_user is not None
        and message.from_user.id == OWNER_ID
    )


@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "🎧 **SUKUNA X MUSIC**\n\n"
        "Welcome! Your radio bot is online.\n\n"
        "🎵 Commands:\n"
        "/play - Start radio\n"
        "/pause - Pause radio\n"
        "/resume - Resume radio\n"
        "/stop - Stop radio\n"
        "/ping - Check bot status\n"
        "/help - Show commands"
    )


@bot.on_message(filters.command("help"))
async def help_command(_, message: Message):
    await message.reply_text(
        "**🎵 SUKUNA X MUSIC HELP**\n\n"
        "/play - Start radio\n"
        "/pause - Pause radio\n"
        "/resume - Resume radio\n"
        "/stop - Stop radio\n"
        "/ping - Check status"
    )


@bot.on_message(filters.command("ping"))
async def ping(_, message: Message):
    await message.reply_text(
        "🏓 **Sukuna X Music is alive!**"
    )


@bot.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):

    if not is_owner(message):
        return await message.reply_text(
            "❌ Only the owner can control the radio."
        )

    chat_id = message.chat.id

    if chat_id in playing_chats:
        return await message.reply_text(
            "🎶 Radio is already playing!"
        )

    try:
        await calls.play(
            chat_id,
            MediaStream(STREAM_URL)
        )

        playing_chats.add(chat_id)

        await message.reply_text(
            "🎶 **Sukuna X Music Radio Started!**"
        )

    except Exception as error:
        logger.exception("Radio playback error")
        await message.reply_text(
            f"❌ Playback failed: {error}"
        )


@bot.on_message(filters.command("pause") & filters.group)
async def pause(_, message: Message):

    if not is_owner(message):
        return await message.reply_text("❌ Owner only.")

    try:
        await calls.pause(message.chat.id)
        await message.reply_text("⏸ Radio paused.")

    except Exception as error:
        logger.exception("Pause error")
        await message.reply_text(f"❌ Error: {error}")


@bot.on_message(filters.command("resume") & filters.group)
async def resume(_, message: Message):

    if not is_owner(message):
        return await message.reply_text("❌ Owner only.")

    try:
        await calls.resume(message.chat.id)
        await message.reply_text("▶️ Radio resumed.")

    except Exception as error:
        logger.exception("Resume error")
        await message.reply_text(f"❌ Error: {error}")


@app.on_message(filters.command("owner"))
async def owner_handler(client, message):
    await message.reply_text(
        "👑 **BOT OWNER INFORMATION**\n\n"
        "Owner: @KingofcursesX\n"
        "🎧 Music Bot Support\n\n"
        "➕ Add me to your Telegram group "
        "and start a voice chat to enjoy music!\n\n"
        "Use /help to see my commands."
    )


@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, message: Message):

    if not is_owner(message):
        return await message.reply_text("❌ Owner only.")

    chat_id = message.chat.id

    try:
        await calls.leave_call(chat_id)
        playing_chats.discard(chat_id)

        await message.reply_text(
            "⏹ **Radio stopped successfully!**"
        )

    except Exception as error:
        logger.exception("Stop error")
        await message.reply_text(f"❌ Error: {error}")


async def main():

    try:
        await bot.start()
        logger.info("Telegram bot started")

        await assistant.start()
        logger.info("Assistant account started")

        await calls.start()
        logger.info("PyTgCalls started")

        print("SUKUNA X MUSIC IS RUNNING!")

        await idle()

    finally:
        await calls.stop()
        await assistant.stop()
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
