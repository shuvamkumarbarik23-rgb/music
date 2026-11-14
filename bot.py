
import asyncio
import json
import logging
from difflib import get_close_matches

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle, filters as call_filters
from pytgcalls.types import StreamEnded

from config import API_ID, API_HASH, STRING_SESSION

logging.basicConfig(level=logging.INFO)

app = Client(
    "sukuna_music",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

calls = PyTgCalls(app)

queues = {}
current = {}


def load_songs():
    with open("songs.json", "r", encoding="utf-8") as f:
        return json.load(f)


def search_song(name):
    songs = load_songs()
    titles = list(songs.keys())

    match = get_close_matches(
        name.lower(),
        [x.lower() for x in titles],
        n=1,
        cutoff=0.45
    )

    if not match:
        return None

    return next(
        songs[x] for x in titles
        if x.lower() == match[0]
    ), next(
        x for x in titles
        if x.lower() == match[0]
    )


async def play_next(chat_id):
    queue = queues.get(chat_id, [])

    if not queue:
        current.pop(chat_id, None)
        await app.send_message(chat_id, "Queue finished!")
        return

    title, url = queue.pop(0)

    try:
        await calls.play(chat_id, url)
        current[chat_id] = title

        await app.send_message(
            chat_id,
            f"🎵 **Now Playing:** {title}"
        )

    except Exception as e:
        logging.exception("Playback failed")
        await app.send_message(
            chat_id,
            f"Playback failed: {e}"
        )


@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "🎧 **Sukuna X Music**\n\n"
        "Use /play song name to play music."
    )


@app.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: /play song name"
        )

    name = message.text.split(maxsplit=1)[1]
    result = search_song(name)

    if not result:
        return await message.reply_text(
            "❌ Song not found in my music library."
        )

    url, title = result
    chat_id = message.chat.id

    if chat_id not in queues:
        queues[chat_id] = []

    if chat_id in current:
        queues[chat_id].append((title, url))
        return await message.reply_text(
            f"➕ Added to queue: **{title}**"
        )

    queues[chat_id].append((title, url))
    await play_next(chat_id)


@app.on_message(filters.command("skip") & filters.group)
async def skip(_, message: Message):
    chat_id = message.chat.id

    if chat_id not in current:
        return await message.reply_text("Nothing is playing.")

    try:
        await calls.leave_call(chat_id)
        current.pop(chat_id, None)
        await play_next(chat_id)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("pause") & filters.group)
async def pause(_, message: Message):
    await calls.pause(message.chat.id)
    await message.reply_text("⏸ Paused.")


@app.on_message(filters.command("resume") & filters.group)
async def resume(_, message: Message):
    await calls.resume(message.chat.id)
    await message.reply_text("▶️ Resumed.")


@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message: Message):
    chat_id = message.chat.id

    queues[chat_id] = []
    current.pop(chat_id, None)

    await calls.leave_call(chat_id)
    await message.reply_text("⏹ Music stopped.")


@app.on_message(filters.command("queue") & filters.group)
async def queue(_, message: Message):
    chat_id = message.chat.id
    songs = queues.get(chat_id, [])

    text = "**🎵 Music Queue**\n\n"

    if chat_id in current:
        text += f"▶️ {current[chat_id]}\n"

    for i, (title, _) in enumerate(songs, 1):
        text += f"{i}. {title}\n"

    await message.reply_text(
        text if current.get(chat_id) or songs
        else "Queue is empty."
    )


@calls.on_update(call_filters.stream_end())
async def stream_end_handler(_, update: StreamEnded):
    chat_id = update.chat_id

    if chat_id in current:
        current.pop(chat_id, None)
        await play_next(chat_id)


if __name__ == "__main__":
    calls.start()
    print("Sukuna X Music Started!")
    idle()
