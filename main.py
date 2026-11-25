
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
    SSL_MESSAGE_FILE,
    LOG_FILE,
    HANES_SSL_WEBHOOK_URL,
)

from services.countdown_vps import create_embed as create_vps_embed
from services.countdown_ssl import create_embed as create_ssl_embed


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

def load_message_id(message_file):
    try:
        with open(message_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("message_id")

    except FileNotFoundError:
        return None

    except (json.JSONDecodeError, OSError):
        logger.exception("Gagal membaca %s", message_file)
        raise


def save_message_id(message_id, message_file):
    temp_file = message_file + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(
            {"message_id": message_id},
            file,
            indent=4,
        )

    os.replace(temp_file, message_file)


# =========================
# COUNTDOWN MANAGER
# =========================

async def update_countdown(webhook, create_embed, message_file, label):

    embed = create_embed()
    message_id = load_message_id(message_file)

    if message_id:
        try:
            await webhook.edit_message(
                message_id,
                embed=embed,
            )

            logger.info(
                "%s countdown berhasil diperbarui | Message ID: %s",
                label,
                message_id,
            )
            return

        except discord.NotFound:
            logger.warning(
                "%s: pesan lama tidak ditemukan. Membuat pesan baru.",
                label,
            )

        except discord.HTTPException:
            logger.exception(
                "%s: gagal mengedit pesan Discord.",
                label,
            )
            raise

    message = await webhook.send(
        embed=embed,
        wait=True,
    )

    save_message_id(message.id, message_file)

    logger.info(
        "%s countdown berhasil dibuat | Message ID: %s",
        label,
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


async def scheduler(webhook, create_embed, message_file, label):

    while True:
        next_run = get_next_run()
        now = datetime.now(HANES_TIMEZONE)

        wait_seconds = (next_run - now).total_seconds()

        logger.info(
            "Next %s countdown update: %s",
            label,
            next_run.strftime("%d-%m-%Y %H:%M:%S WIB"),
        )

        await asyncio.sleep(wait_seconds)

        try:
            await update_countdown(webhook, create_embed, message_file, label)

        except Exception:
            logger.exception(
                "%s countdown update gagal. Akan dicoba pada jadwal berikutnya.",
                label,
            )


# =========================
# MAIN
# =========================

async def run_countdown(webhook_url, create_embed, message_file, label):
    if not webhook_url:
        raise ValueError(f"Webhook URL untuk {label} belum diatur.")

    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        webhook = discord.Webhook.from_url(
            webhook_url,
            session=session,
        )

        logger.info("%s countdown started.", label)

        # Buat pesan pertama atau sinkronisasi pesan lama
        try:
            await update_countdown(webhook, create_embed, message_file, label)

        except Exception:
            logger.exception(
                "Initial %s countdown update gagal.",
                label,
            )
            raise

        # Jalankan scheduler
        await scheduler(webhook, create_embed, message_file, label)


async def main():
    if not HANES_SSL_WEBHOOK_URL:
        raise ValueError(
            "HANES_SSL_WEBHOOK_URL is not set in the environment variables."
        )

    await asyncio.gather(
        run_countdown(
            HANES_LICENSING_WEBHOOK_URL,
            create_vps_embed,
            MESSAGE_FILE,
            "Hanes VPS License",
        ),
        run_countdown(
            HANES_SSL_WEBHOOK_URL,
            create_ssl_embed,
            SSL_MESSAGE_FILE,
            "Hanes SSL Certificate",
        ),
    )


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Hanes countdowns stopped.")
