from datetime import datetime
from zoneinfo import ZoneInfo


import discord

from config import (
    HANES_NAME,
    HANES_EXPIRY_DATE,
    HANES_TIMEZONE,
    HANES_LICENSING_WEBHOOK_URL,  
)

def calculate_countdown():
    now = datetime.now(HANES_TIMEZONE)
    today = now.date()

    remaining_days = (HANES_EXPIRY_DATE - today).days

    if remaining_days < 0:
        status = "EXPIRED"
        color = discord.Color.dark_grey()
        description = f"VPS license has expired on {HANES_EXPIRY_DATE}."

    elif remaining_days == 0:
        status = "EXPIRES TODAY"
        color = discord.Color.red()
        description = f"VPS license expires today!."

    elif remaining_days <= 1:
        status = "URGENT"
        color = discord.Color.orange()
        description = f"VPS license expires tomorrow!."

    elif remaining_days <= 3:
        status = "CRITICAL"
        color = discord.Color.orange()
        description = f"VPS license expires in {remaining_days} days."

    elif remaining_days <= 7:
        status = "WARNING"
        color = discord.Color.yellow()
        description = f"VPS license expires in {remaining_days} days."

    elif remaining_days <= 14:
        status = "NOTICE"
        color = discord.Color.blue()
        description = f"VPS license expires in {remaining_days} days."

    else:
        status = "ACTIVE"
        color = discord.Color.green()
        description = f"VPS license is valid for {remaining_days} more days."

    return {
        "name": "HANES VPS",
        "remaining_days": remaining_days,
        "status": status,
        "color": color,             
        "description": description,
        "updated_at": now,
        "expiry_date": HANES_EXPIRY_DATE
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
        title=f"{data['name']} License Countdown",
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
        name="Expired Date",
        value=data["expiry_date"].strftime("%d %B %Y"),
        inline=True,
    )

    embed.add_field(
        name="License Status",
        value=f"**{data['status']}**",
        inline=True,
    )

    # embed.set_footer(
    #     text="Hanes VPS License Monitor"
    # )

    return embed



