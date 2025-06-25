#!/usr/bin/env python3
import logging
import time

import catcher.constants as const
from catcher.catcher import Catcher
from catcher.catcher_report import CatcherReport


def main():
    # teardown=False = debug mode
    with Catcher(teardown=True) as bot:
        bot.login()
        bot.next_page()

        # 6 hours. 60sec * 60mins * 6hours
        target_time = 60 * 60 * 60
        time_start = time.time()

        psych = const.PSYCHOLOGISTS[0]
        while (time.time() - time_start) < target_time:
            if bot.search_for_a_slot(psych):
                bot.make_report(psych)
                return 0
            bot.refresh()
            bot.next_page()

        logging.warning("couldn't find a psych")
        CatcherReport().send_msg("Не нашел слот")


if __name__ == "__main__":
    main()
