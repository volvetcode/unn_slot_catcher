#!/usr/bin/env python3
import logging
import time

import catcher.constants as const
from catcher.catcher import Catcher
from catcher.catcher_report import CatcherReport


def main():
    # teardown=False = debug mode
    try:
        with Catcher(teardown=True) as bot:
            bot.login()
            bot.next_page()

            # 6 hours. 60sec * 60mins * 8hours
            target_time = 60 * 60 * 8
            time_start = time.time()

            found_slot = False
            psych = const.PSYCHOLOGISTS[0]
            while (time.time() - time_start) < target_time:
                if bot.search_for_a_slot(psych):
                    found_slot = True
                    break
                bot.refresh()
                bot.next_page()

            if found_slot:
                bot.make_report(psych, found_slot=found_slot)
            else:
                bot.make_report(psych, found_slot=found_slot)
                logging.warning(
                    f"couldn't find a psychologist in {target_time / 60 / 60:.2f}hours"
                )
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
