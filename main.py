
import asyncio
import json
import logging
import os

from datetime import datetime, timedelta

import aiohttp
import discord

from config import (
    HANES_LICENSING_WEBHOOK_URL,
    HANES_TIMEZONE,
    UPDATE_HOUR,
    UPDATE_MINUTE,
    MESSAGE_FILE,
    LOG_FILE,
)

from services.countdown import create_embed


# =========================
# LOGGING
# =========================

os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("HanesCountdown")


# =========================
# MESSAGE STORAGE
# =========================

def load_message_id():
    try:
        with open(MESSAGE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("message_id")

    except FileNotFoundError:
        return None

    except (json.JSONDecodeError, OSError):
        logger.exception("Gagal membaca message.json")
        raise


def save_message_id(message_id):
    temp_file = MESSAGE_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(
            {"message_id": message_id},
            file,
            indent=4,
        )

    os.replace(temp_file, MESSAGE_FILE)


# =========================
# COUNTDOWN MANAGER
# =========================

async def update_countdown(webhook):

    embed = create_embed()
    message_id = load_message_id()

    if message_id:
        try:
            await webhook.edit_message(
                message_id,
                embed=embed,
            )

            logger.info(
                "Countdown berhasil diperbarui | Message ID: %s",
                message_id,
            )
            return

        except discord.NotFound:
            logger.warning(
                "Pesan lama tidak ditemukan. Membuat pesan baru."
            )

        except discord.HTTPException:
            logger.exception(
                "Gagal mengedit pesan Discord."
            )
            raise

    message = await webhook.send(
        embed=embed,
        wait=True,
    )

    save_message_id(message.id)

    logger.info(
        "Countdown berhasil dibuat | Message ID: %s",
        message.id,
    )


# =========================
# SCHEDULER
# =========================

def get_next_run():
    now = datetime.now(HANES_TIMEZONE)

    next_run = now.replace(
        hour=UPDATE_HOUR,
        minute=UPDATE_MINUTE,
        second=0,
        microsecond=0,
    )

    if next_run <= now:
        next_run += timedelta(days=1)

    return next_run


async def scheduler(webhook):

    while True:
        next_run = get_next_run()
        now = datetime.now(HANES_TIMEZONE)

        wait_seconds = (next_run - now).total_seconds()

        logger.info(
            "Next countdown update: %s",
            next_run.strftime("%d-%m-%Y %H:%M:%S WIB"),
        )

        await asyncio.sleep(wait_seconds)

        try:
            await update_countdown(webhook)

        except Exception:
            logger.exception(
                "Countdown update gagal. Akan dicoba pada jadwal berikutnya."
            )


# =========================
# MAIN
# =========================

async def main():

    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        webhook = discord.Webhook.from_url(
            HANES_LICENSING_WEBHOOK_URL,
            session=session,
        )

        logger.info("Hanes VPS License Countdown started.")

        # Buat pesan pertama atau sinkronisasi pesan lama
        try:
            await update_countdown(webhook)

        except Exception:
            logger.exception(
                "Initial countdown update gagal."
            )
            raise

        # Jalankan scheduler
        await scheduler(webhook)


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("HanesVPS Countdown stopped.")
