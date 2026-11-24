import os
from datetime import date
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

#discord
HANES_LICENSING_WEBHOOK_URL = os.getenv("HANES_LICENSING_WEBHOOK_URL")

# License
HANES_NAME = "Hanes VPS"
HANES_EXPIRY_DATE = date.fromisoformat(
    os.getenv("HANES_EXPIRY_DATE", "2027-02-14")
    )

# Timezone
HANES_TIMEZONE = ZoneInfo(
    os.getenv("HANES_TIMEZONE", "Asia/Jakarta")
    )

# scheduler
UPDATE_HOUR = int(os.getenv("UPDATE_HOUR", 0))
UPDATE_MINUTE = int(os.getenv("UPDATE_MINUTE", 30))

#Storage
MESSAGE_FILE = "data/message.json"
LOG_FILE = "logs/countdown.log"

if not HANES_LICENSING_WEBHOOK_URL:
    raise ValueError("HANES_LICENSING_WEBHOOK_URL is not set in the environment variables.")

if not 0 <= UPDATE_HOUR < 24:
    raise ValueError("UPDATE_HOUR must be between 0 and 23.")

if not 0 <= UPDATE_MINUTE < 59:
    raise ValueError("UPDATE_MINUTE must be between 0 and 59.")