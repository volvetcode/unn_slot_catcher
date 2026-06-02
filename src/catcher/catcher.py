import logging
import os
import sys
from time import sleep, time
import pytest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import catcher.constants as const
from catcher.notifier import Notifier
from catcher.config import Settings

# from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(const.LOG_PATH, mode="w")
file_handler.setFormatter(
    logging.Formatter('"%(asctime)s","%(levelname)s","%(message)s"')
)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(
    logging.Formatter('"%(asctime)s","%(levelname)s","%(message)s"')
)

logger.handlers = [file_handler, stream_handler]


class Catcher(webdriver.Chrome):
    def __init__(
        self,
        settings: Settings,
        notifier: Notifier,
        driver_path=const.CHROMEDRIVER_PATH,
        teardown=False,
    ):
        self.notifier = notifier
        self.settings = settings

        logging.info("setting up...")
        # i don't know why but it did work a couple of times without a webdriver
        # better be safe than sorry
        if os.path.exists(driver_path):
            logging.info("found ChromeDriver")
        else:
            logging.critical(f"ChromeDriver not found at {driver_path}")
            raise FileNotFoundError(f"ChromeDriver not found at {driver_path}")

        self.driver_path = driver_path
        os.environ["PATH"] += driver_path
        self.teardown = teardown

        self.psychologists = const.PSYCHOLOGISTS
        self.retries = 3
        self.duration_hours = 8
        self.psych_index = 0
        self.psych = self.psychologists[self.psych_index]

        options = webdriver.ChromeOptions()
        options.add_argument(
            "user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15'"
        )
        options.add_argument("Accept-Language='en-GB,en;q=0.9'")

        if self.teardown:
            logging.info("running in production mode")
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
        else:
            # detach is used for the chrome window to stay open.
            # doesnt work without __exit__ func
            logging.info("running in debug mode")
            options.add_experimental_option("detach", True)
        # suppresses unnecessary logging messages from ChromeDriver
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        options.add_argument("--disable-extensions")
        options.add_argument("--avoid-stats")  # avoid sending data to plausible
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        super().__init__(options=options)
        self.implicitly_wait(15)
        self.parse_args(sys.argv)
        # hours to seconds
        self.target_time = 60 * 60 * self.duration_hours
        logging.info("finished setting up")

    # works hand to hand with detach.
    # important. don't remove
    def __exit__(self, exc_type, exc, traceback):
        logging.info("quitting")
        if self.teardown:
            self.quit()
            return

    def parse_args(self, argv):
        n_argv = len(argv)
        if n_argv < 4:
            if n_argv > 1:
                try:
                    self.duration_hours = float(argv[1])
                except Exception as e:
                    logging.warning(e)
                    logging.warning("invalid duration, using default 8 hours")

            if n_argv > 2:
                try:
                    self.psych_index = int(argv[2])
                    self.psych = self.psychologists[self.psych_index]
                except Exception as e:
                    logging.warning(e)
                    logging.warning(
                        "invalid psychologist, we will look for psychologist №0"
                    )

        else:
            logging.warning("too many arguments. running in default mode")

        logging.info(f"the script will run for {self.duration_hours} hours")
        logging.info(f"the script will look for {self.psychologists[self.psych_index]}")

    def login(self):
        """
        Authenticate user with retry logic.

        Has a 60 second delay in between retries.
        We need that because the website goes down when
        psychologists update the slots

        Raises:
            Exception: if login fails after all retry attempts
                or an unexpected error occurs
        """
        logging.info("Logging in...")

        for attempt in range(1, self.retries + 1):
            try:
                self._attempt_login()
                logging.info(f"Logged in successfully on attempt №{attempt}")
                return
            except NoSuchElementException:
                logging.warning(f"Failed to login. Attempt №{attempt}")
                sleep(60)
            except Exception as e:
                logging.critical(f"Unexpected error on attempt №{attempt}: {e}")
                raise Exception(f"Unexpected error: {e}")

        logging.critical("Could not login after all retries")
        raise Exception("Couldn't login")

    def _attempt_login(self):
        """
        Execute a single login attempt.

        Open the website, fill in the credentials,
        Try to press the login button.

        Verifies if we logged in with pytest
        """
        self.get(const.BASE_URL)
        self.find_element(By.ID, "mat-input-0").send_keys(const.LOGIN)
        self.find_element(By.ID, "mat-input-1").send_keys(const.PASSWORD)
        sleep(2)
        self.find_element(By.XPATH, "//button[span[text()='ВОЙТИ']]").click()
        sleep(2)

        # Verify login success by checking that the login button is gone
        with pytest.raises(NoSuchElementException):
            self.find_element(By.XPATH, "//button[span[text()='ВОЙТИ']]")

    def next_page(self):
        # WebDriverWait(self, 30).until()
        logging.info("going to the next page in schedule")
        flag = 1
        for attempt in range(1, self.retries + 1):
            try:
                next_week_button = self.find_element(By.CLASS_NAME, "week-next")
                next_week_button.click()
                flag = 0
                break
            except NoSuchElementException:
                logging.warning(f"failed to go to the next page. attempt№{attempt}")
            except Exception as e:
                logging.critical(f"Unexpected error: {e}")
                raise Exception(f"Unexpected error: {e}")

        if flag:
            logging.critical("Couldn't go to the next page")
            raise Exception("Couldn't go to the next page")

    # no need to define refresh.
    # self.refresh() will work fine

    def search_for_a_slot(self, psychologist):
        logging.info(f"searching for {psychologist}")
        try:
            self.find_element(
                By.XPATH, f"//div[normalize-space(text())='{psychologist}']"
            )
            logging.info(f"found {psychologist}")
            return True
        except NoSuchElementException:
            logging.info(f"didn't find {psychologist}")
            return False
        except Exception as e:
            logging.error(
                f"Unexpected error searching for {psychologist}: {e}", exc_info=True
            )
            return False

    def make_report(self, psych, found_slot=False):
        try:
            if found_slot:
                msg = f"{psych} открыла слот. Бегом записываться!"
            else:
                msg = f"{psych} не открыла слот"
                logging.warning("couldn't find a psychologist")

            self.notifier.send(msg)
        except Exception as exc:
            logging.error(f"couldn't make a report. Error: {exc}")

    def monitor(self):
        """Main monitoring loop - handles login, searching, and reporting"""
        self.login()

        found_slot = False
        time_start = time()

        while (time() - time_start) < self.target_time:
            try:
                self.refresh()
                try:
                    self.next_page()
                except Exception:
                    # If next_page fails, try to re-login and continue
                    try:
                        self.login()
                        continue
                    except Exception:
                        break
            except Exception:
                break

            if self.search_for_a_slot(self.psych):
                found_slot = True
                break

        self.make_report(self.psych, found_slot=found_slot)

        total_time = (time() - time_start) / 60
        logging.info(
            f"Statistics: runtime={total_time:.0f}mins, slot_found={found_slot} for {self.psych}"
        )
