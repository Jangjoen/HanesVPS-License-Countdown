from datetime import datetime

import discord

from config import (
    HANES_SSL_EXPIRY_DATE,
    HANES_SSL_NAME,
    HANES_TIMEZONE,
)


def calculate_countdown():
    now = datetime.now(HANES_TIMEZONE)
    remaining_days = (HANES_SSL_EXPIRY_DATE - now.date()).days

    if remaining_days < 0:
        status = "EXPIRED"
        color = discord.Color.dark_grey()
        description = (
            f"{HANES_SSL_NAME} certificate expired on "
            f"{HANES_SSL_EXPIRY_DATE}."
        )
    elif remaining_days == 0:
        status = "EXPIRES TODAY"
        color = discord.Color.red()
        description = f"{HANES_SSL_NAME} certificate expires today!"
    elif remaining_days == 1:
        status = "URGENT"
        color = discord.Color.orange()
        description = f"{HANES_SSL_NAME} certificate expires tomorrow!"
    elif remaining_days <= 3:
        status = "CRITICAL"
        color = discord.Color.orange()
        description = (
            f"{HANES_SSL_NAME} certificate expires in {remaining_days} days."
        )
    elif remaining_days <= 7:
        status = "WARNING"
        color = discord.Color.yellow()
        description = (
            f"{HANES_SSL_NAME} certificate expires in {remaining_days} days."
        )
    elif remaining_days <= 14:
        status = "NOTICE"
        color = discord.Color.blue()
        description = (
            f"{HANES_SSL_NAME} certificate expires in {remaining_days} days."
        )
    else:
        status = "ACTIVE"
        color = discord.Color.green()
        description = (
            f"{HANES_SSL_NAME} certificate is valid for "
            f"{remaining_days} more days."
        )

    return {
        "name": HANES_SSL_NAME,
        "remaining_days": remaining_days,
        "status": status,
        "color": color,
        "description": description,
        "updated_at": now,
        "expiry_date": HANES_SSL_EXPIRY_DATE,
    }


def create_embed():
    data = calculate_countdown()
    days = data["remaining_days"]

    if days < 0:
        countdown_text = f"EXPIRED ({abs(days)} hari lalu)"
    elif days == 0:
        countdown_text = "EXPIRES TODAY"
    else:
        countdown_text = f"{days} HARI LAGI"

    embed = discord.Embed(
        title=f"{data['name']} Certificate Countdown",
        description=data["description"],
        color=data["color"],
        timestamp=data["updated_at"],
    )
    embed.add_field(
        name="Remaining Time",
        value=f"**{countdown_text}**",
        inline=False,
    )
    embed.add_field(
        name="Expiry Date",
        value=data["expiry_date"].strftime("%d %B %Y"),
        inline=True,
    )
    embed.add_field(
        name="Certificate Status",
        value=f"**{data['status']}**",
        inline=True,
    )
    embed.set_footer(text="https://pthsci.com/")

    return embed