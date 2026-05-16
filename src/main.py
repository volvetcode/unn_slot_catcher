#!/usr/bin/env python3
import logging
import sys

from catcher.catcher import Catcher


def main():
    try:
        with Catcher(teardown=True) as bot:
            bot.monitor()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
