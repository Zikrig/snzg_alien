import logging
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "bot.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)
logger.info("Starting bots, log file: %s", LOG_FILE)


def f1():
    import vk


def f2():
    import tg


t1 = threading.Thread(target=f1, name="vk-bot")
t2 = threading.Thread(target=f2, name="tg-bot")

t1.start()
t2.start()
