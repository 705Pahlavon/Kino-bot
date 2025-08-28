import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

API_TOKEN = os.getenv("7995399712:AAGNYfjcoPkmhWhtfWCRwRRozfWnylGpK8I")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7500535752"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

CHANNELS_FILE = "channels.json"
FILMS_FILE = "films.json"

def load_channels():
    try:
        with open(CHANNELS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_channels(channels):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(channels, f)

def load_films():
    try:
        with open(FILMS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_films(films):
    with open(FILMS_FILE, "w") as f:
        json.dump(films, f)

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    channels = load_channels()
    if not await check_subscriptions(message.from_user.id, channels):
        await message.answer("❌ Avval quyidagi kanallarga obuna bo‘ling:")
        for ch in channels:
            await message.answer(f"👉 {ch}")
        return
    await message.answer("Salom 🎬\nFilm kodini yuboring (masalan: A001)")

@dp.message_handler()
async def handle_msg(message: types.Message):
    if message.from_user.id == ADMIN_ID and message.text.startswith("/addfilm"):
        try:
            _, code, link = message.text.split(" ", 2)
            films = load_films()
            films[code] = link
            save_films(films)
            await message.answer(f"✅ {code} filmi qo‘shildi")
        except:
            await message.answer("❌ Format: /addfilm KOD LINK")
        return

    if message.from_user.id == ADMIN_ID and message.text.startswith("/addchannel"):
        try:
            _, channel = message.text.split(" ", 1)
            channels = load_channels()
            if channel not in channels:
                channels.append(channel)
                save_channels(channels)
            await message.answer(f"✅ {channel} majburiy obunaga qo‘shildi")
        except:
            await message.answer("❌ Format: /addchannel @kanal")
        return

    channels = load_channels()
    if not await check_subscriptions(message.from_user.id, channels):
        await message.answer("❌ Avval kanallarga obuna bo‘ling!")
        return

    films = load_films()
    code = message.text.strip()
    if code in films:
        await message.answer(f"🎥 Mana film:\n{films[code]}")
    else:
        await message.answer("❌ Bunday film kodi topilmadi.")

async def check_subscriptions(user_id, channels):
    for channel in channels:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 5000))

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
