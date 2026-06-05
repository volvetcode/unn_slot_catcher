import os
import logging

from selenium import webdriver

from catcher.config import Settings


def configure_options(settings: Settings) -> webdriver.ChromeOptions:
    """Configures options for webdriver based on Settings"""
    options = webdriver.ChromeOptions()

    # production settings = headless browser
    # dev settings = visible browser
    if settings.is_prod:
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')

    # add user-agent and language to not get caught by bot catchers
    options.add_argument(
        "user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15'"
    )
    options.add_argument("Accept-Language='en-GB,en;q=0.9'")

    # disable unnecessary stuff
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--disable-extensions')
    options.add_argument('--avoid-stats')
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    return options


def create_driver(settings: Settings) -> webdriver.Chrome:
    if not os.path.exists(settings.chromedriver_path):
        logging.error("Path to chromedriver doesn't exist")
        raise FileNotFoundError()

    options = configure_options(settings=settings)
    service = webdriver.chrome.service.Service(
        executable_path=settings.chromedriver_path
    )
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(settings.time_to_wait)

    return driver
