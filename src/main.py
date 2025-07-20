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
        with Catcher(teardown=False) as bot:
            bot.login()

            found_slot = False
            time_start = time.time()

            while (time.time() - time_start) < bot.target_time:
                try:
                    bot.refresh()
                    bot.next_page()
                except:
                    break

                if bot.search_for_a_slot(bot.psych):
                    found_slot = True
                    break


            bot.make_report(bot.psych, found_slot=found_slot)

            total_time = (time.time() - time_start) / 60
            logging.info(f"Statistics: runtime={total_time:.0f}mins")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
