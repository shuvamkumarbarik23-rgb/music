
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sukuna-x-music")

# Telegram command bot
bot = Client(
    "sukuna_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# User account for voice chat
assistant = Client(
    "sukuna_assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

calls = PyTgCalls(assistant)

playing_chats = set()


def is_owner(message):
    return (
        message.from_user is not None
        and message.from_user.id == OWNER_ID
    )


@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "🎧 **SUKUNA X MUSIC**\n\n"
        "Your music radio bot is online!\n\n"
        "/play - Start radio\n"
        "/pause - Pause radio\n"
        "/resume - Resume radio\n"
        "/stop - Stop radio\n"
        "/ping - Check bot status"
    )


@bot.on_message(filters.command("ping"))
async def ping(_, message: Message):
    await message.reply_text("🏓 Sukuna X Music is online!")


@bot.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):

    if not is_owner(message):
        return await message.reply_text("❌ Owner only command.")

    if len(message.command) > 1:
        return await message.reply_text(
            "This configuration supports radio streaming, "
            "not song-name searching yet.\n"
            "Use /play to start the radio."
        )

    chat_id = message.chat.id

    try:
        await calls.play(
            chat_id,
            MediaStream(STREAM_URL)
        )

        playing_chats.add(chat_id)

        await message.reply_text(
            "🎶 **Sukuna X Music Radio Started!**"
        )

    except Exception as e:
        logger.exception("Play error")
        await message.reply_text(f"❌ Error: {e}")


@bot.on_message(filters.command("pause") & filters.group)
async def pause(_, message: Message):

    if not is_owner(message):
        return await message.reply_text("❌ Owner only command.")

    try:
        await calls.pause(message.chat.id)
        await message.reply_text("⏸ Radio paused.")

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


@bot.on_message(filters.command("resume") & filters.group)
async def resume(_, message: Message):

    if not is_owner(message):
        return await message.reply_text("❌ Owner only command.")

    try:
        await calls.resume(message.chat.id)
        await message.reply_text("▶️ Radio resumed.")

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, message: Message):

    if not is_owner(message):
        return await message.reply_text("❌ Owner only command.")

    try:
        await calls.leave_call(message.chat.id)
        playing_chats.discard(message.chat.id)

        await message.reply_text("⏹ Radio stopped.")

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


async def main():
    await bot.start()
    await assistant.start()
    await calls.start()

    logger.info("Sukuna X Music started successfully!")

    await idle()

    await calls.stop()
    await assistant.stop()
    await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
