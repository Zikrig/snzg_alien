import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
VK_GROUP_TOKEN = os.environ["VK_GROUP_TOKEN"]
VK_GROUP_ID = os.environ["VK_GROUP_ID"]
VK_API_VERSION = os.getenv("VK_API_VERSION", "5.120")

GOOGLE_SHEETS_URL = os.getenv(
    "GOOGLE_SHEETS_URL",
    "https://docs.google.com/spreadsheets/d/1FhYGE5IODqbtXSfQGBs0BGUaUJYAWBGAC2SRWqYzf6M",
)
_google_creds = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    "credentials/google-service-account.json",
)
GOOGLE_SERVICE_ACCOUNT_FILE = (
    _google_creds
    if os.path.isabs(_google_creds)
    else str(BASE_DIR / _google_creds)
)

ADMIN_SECRET = os.environ["ADMIN_SECRET"]

TELEGRAM_CHANNEL_USERNAME = os.getenv("TELEGRAM_CHANNEL_USERNAME", "@skidkinezagorami")
TELEGRAM_CHANNEL_INVITE_URL = os.getenv(
    "TELEGRAM_CHANNEL_INVITE_URL",
    "https://t.me/+Y3yWMfv1z9FmZGM6",
)
TELEGRAM_CHANNEL_PUBLIC_URL = os.getenv(
    "TELEGRAM_CHANNEL_PUBLIC_URL",
    "https://t.me/skidkinezagorami",
)


def admin_command(name: str) -> str:
    return f"{name}_{ADMIN_SECRET}"
