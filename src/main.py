#!/usr/bin/env python3
import logging
import time
import sys

import catcher.constants as const
from catcher.catcher import Catcher
from catcher.catcher_report import CatcherReport


def main(argv):
    duration_hours = 8
    psychologist_index = 0

    n_argv = len(argv)
    if n_argv < 4:
        if n_argv > 1:
            try:
                duration_hours = float(sys.argv[1])
            except:
                logging.warning('invalid duration, using default 8 hours')
        
        if n_argv > 2:
            try:
                psych_index = int(sys.argv[2])
            except:
                logging.warning('invalid psychologist, we will look for psychologist №0')
        
    else:
        logging.warning("too many arguments. running in default mode")

    logging.info(f'the script will run for {duration_hours} hours')
    logging.info(f'we are looking for {const.PSYCHOLOGISTS[psych_index]}')

    try:
        # teardown=False = debug mode
        with Catcher(teardown=True) as bot:
            bot.login()
            bot.next_page()

            # hours to seconds 
            target_time = 60 * 60 * duration_hours
            time_start = time.time()

            found_slot = False
            psych = const.PSYCHOLOGISTS[psychologist_index]
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
                    f"couldn't find a psychologist"
                )

            total_time = (time.time() - time_start) / 60
            logging.info(f"Statistics: runtime={total_time:.0f}mins")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main(sys.argv)
