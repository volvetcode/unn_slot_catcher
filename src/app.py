import logging
import sys

from catcher import Catcher


def main() -> None:
    try:
        with Catcher() as bot:
            bot.monitor()
    except Exception as e:
        logging.error(f'Fatal error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
