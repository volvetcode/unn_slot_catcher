import logging
import sys

from catcher import Catcher
from catcher.config import get_settings
from catcher.notifier import TelegramNotifier


def main() -> None:
    settings = get_settings()

    notifier = TelegramNotifier(
        token=settings.telegram_token,
        chat_id=settings.chat_id,
    )

    try:
        with Catcher(settings=settings, notifier=notifier, teardown=True) as bot:
            bot.monitor()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
