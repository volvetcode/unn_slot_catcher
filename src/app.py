import logging
import sys

from catcher import Catcher
from catcher.notifier import TelegramNotifier

import catcher.constants as const


def main() -> None:
    notifier = TelegramNotifier(token=const.TELEGRAM_TOKEN, chat_id=const.CHAT_ID)

    try:
        with Catcher(notifier=notifier, teardown=True) as bot:
            bot.monitor()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
