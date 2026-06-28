import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
import atexit

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "bot.log"
LOCK_FILE = LOG_DIR / "bot.lock"

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


def _release_lock():
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        # Логировать не обязательно при завершении процесса
        pass


def _pid_is_running(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    else:
        return True


def acquire_lock_or_exit():
    """
    Гарантирует, что одновременно запущен только один экземпляр этого приложения.
    Если lock-файл уже существует, процесс завершается с ошибкой.
    """
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            logger.warning("Removing invalid lock file %s", LOCK_FILE)
            LOCK_FILE.unlink(missing_ok=True)
        else:
            # В Docker главный процесс всегда PID 1: после crash/restart lock с «1»
            # остаётся на диске, а новый процесс снова pid=1 — os.kill(1,0) «успешен».
            if old_pid == os.getpid():
                logger.warning(
                    "Removing stale lock file %s (pid %s matches current process, likely container restart)",
                    LOCK_FILE,
                    old_pid,
                )
                LOCK_FILE.unlink(missing_ok=True)
            elif _pid_is_running(old_pid):
                logger.error(
                    "Lock file %s is held by running process %s. Exiting.",
                    LOCK_FILE,
                    old_pid,
                )
                sys.exit(1)
            else:
                logger.warning(
                    "Removing stale lock file %s (pid %s is not running)",
                    LOCK_FILE,
                    old_pid,
                )
                LOCK_FILE.unlink(missing_ok=True)

    try:
        fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except FileExistsError:
        logger.error("Lock file %s already exists — another bot instance is running. Exiting.", LOCK_FILE)
        sys.exit(1)
    except Exception:
        logger.exception("Failed to create lock file %s. Exiting to avoid multiple instances.", LOCK_FILE)
        sys.exit(1)

    atexit.register(_release_lock)
    logger.info("Instance lock acquired: %s", LOCK_FILE)


def f1():
    import vk


def f2():
    from tg.bot import start_polling

    start_polling()


def main():
    acquire_lock_or_exit()

    t1 = threading.Thread(target=f1, name="vk-bot")
    t2 = threading.Thread(target=f2, name="tg-bot")

    t1.start()
    t2.start()

    t1.join()
    t2.join()


if __name__ == "__main__":
    main()
