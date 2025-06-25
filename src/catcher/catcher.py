import os

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

import catcher.constants as const
from catcher.catcher_report import CatcherReport

# from selenium.webdriver.support.ui import WebDriverWait


class Catcher(webdriver.Chrome):
    def __init__(self, driver_path=const.CHROMEDRIVER_PATH, teardown=False):
        self.driver_path = driver_path
        os.environ["PATH"] += driver_path
        self.teardown = teardown

        self.psychologists = {name: False for name in const.PSYCHOLOGISTS}

        options = webdriver.ChromeOptions()
        options.add_argument(
            "user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15'"
        )
        options.add_argument("Accept-Language='en-GB,en;q=0.9'")

        if self.teardown == True:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
        else:
            # detach is used for the chrome window to stay open.
            # doesnt work without __exit__ func
            options.add_experimental_option("detach", True)
        # suppresses unnecessary logging messages from ChromeDriver
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        super().__init__(options=options)
        self.implicitly_wait(15)

    # works hand to hand with detach.
    # important. don't remove
    def __exit__(self, exc_type, exc, traceback):
        if self.teardown:
            self.quit()

    def login(self):
        self.get(const.BASE_URL)
        self.find_element(By.ID, "mat-input-0").send_keys(const.LOGIN)
        self.find_element(By.ID, "mat-input-1").send_keys(const.PASSWORD)
        self.find_element(By.XPATH, "//button[span[text()='ВОЙТИ']]").click()

    def next_page(self):
        # WebDriverWait(self, 30).until()
        next_week_button = self.find_element(By.CLASS_NAME, "week-next")
        next_week_button.click()

    # no need to define refresh.
    # self.refresh() will work fine

    def search_for_a_slot(self, psychologist):
        try:
            slot = self.find_element(
                By.XPATH, f"//div[normalize-space(text())='{psychologist}']"
            )
            return True
        except:
            return False

    def make_report(self, psych):
        report = CatcherReport()
        report.send_msg(f"{psych} открыла слот. Бегом записываться!")

    # future functionality not sure if i will make it
    # def search_for_psychologists(self):
    #     for psych in self.psychologists:
    #         if self.psychologists[psych] == False:
    #             self.psychologists[psych] = \
    #                 self.search_for_a_slot(psych)

    # def make_report(self):
    #     report = CatcherReport(self.psychologists)
    #     report.send_msg(report.report_results())
