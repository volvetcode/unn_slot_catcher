import logging
import os
import sys

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import catcher.constants as const
from catcher.catcher_report import CatcherReport

# from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(const.LOG_PATH, mode="w")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)

logger.handlers = [file_handler, stream_handler]


class Catcher(webdriver.Chrome):
    def __init__(self, driver_path=const.CHROMEDRIVER_PATH, teardown=False):
        logging.info("setting up...")
        # i don't know why but it did work a couple of times without a webdriver
        # better be safe than sorry
        if os.path.exists(driver_path):
            logging.info(f"found ChromeDriver")
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

        if self.teardown == True:
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
                except:
                    logging.warning("invalid duration, using default 8 hours")

            if n_argv > 2:
                try:
                    self.psych_index = int(argv[2])
                    self.psych = self.psychologists[self.psych_index]
                except:
                    logging.warning(
                        "invalid psychologist, we will look for psychologist №0"
                    )

        else:
            logging.warning("too many arguments. running in default mode")

        logging.info(f"the script will run for {self.duration_hours} hours")
        logging.info(f"the script will look for {self.psychologists[self.psych_index]}")

    def login(self):
        logging.info("logging in...")
        flag = 1
        for attempt in range(1, self.retries + 1):
            try:
                self.get(const.BASE_URL)
                self.find_element(By.ID, "mat-input-0").send_keys(const.LOGIN)
                self.find_element(By.ID, "mat-input-1").send_keys(const.PASSWORD)
                self.find_element(By.XPATH, "//button[span[text()='ВОЙТИ']]").click()
                logging.info("logged in")
                flag = 0
                break
            except NoSuchElementException:
                logging.warning(f"failed to login. attempt№{attempt}")
            except Exception as e:
                logging.critical(f"Unexpected error: {e}")
                raise Exception(f"Unexpected error: {e}")

        if flag:
            logging.critical("Couldn't login")
            raise Exception("Couldn't login")

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
            slot = self.find_element(
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
            report = CatcherReport()
            if found_slot:
                msg = f"{psych} открыла слот. Бегом записываться!"
            else:
                msg = f"{psych} не открыла слот"
            report.send_msg(msg)
        except:
            logging.error("couldn't make a report")

    # future functionality not sure if i will make it
    # def search_for_psychologists(self):
    #     for psych in self.psychologists:
    #         if self.psychologists[psych] == False:
    #             self.psychologists[psych] = \
    #                 self.search_for_a_slot(psych)

    # def make_report(self):
    #     report = CatcherReport(self.psychologists)
    #     report.send_msg(report.report_results())
