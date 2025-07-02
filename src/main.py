#!/usr/bin/env python3
import logging
import sys
import time

import catcher.constants as const
from catcher.catcher import Catcher
from catcher.catcher_report import CatcherReport


def main():
    try:
        # teardown=False = debug mode
        with Catcher(teardown=True) as bot:
            bot.login()
            bot.next_page()

            # hours to seconds
            target_time = 60 * 60 * bot.duration_hours
            time_start = time.time()

            found_slot = False
            while (time.time() - time_start) < target_time:
                if bot.search_for_a_slot(bot.psych):
                    found_slot = True
                    break
                bot.refresh()
                bot.next_page()

            if found_slot:
                bot.make_report(bot.psych, found_slot=found_slot)
            else:
                bot.make_report(bot.psych, found_slot=found_slot)
                logging.warning(f"couldn't find a psychologist")

            total_time = (time.time() - time_start) / 60
            logging.info(f"Statistics: runtime={total_time:.0f}mins")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
