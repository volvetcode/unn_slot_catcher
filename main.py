import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from telebot import TeleBot

load_dotenv()
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
PSYCHOLOGIST_NAME = os.getenv("PSYCHOLOGIST_NAME")


def main():
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    driver.get("https://psys.unn.ru/home")
    driver.find_element(By.ID, "mat-input-0").send_keys(LOGIN)
    driver.find_element(By.ID, "mat-input-1").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[span[text()='ВОЙТИ']]").click()
    bot = TeleBot(token=TELEGRAM_TOKEN)

    while True:
        time.sleep(1)
        next_week_button = driver.find_element(By.CLASS_NAME, "week-next")
        next_week_button.click()

        try:
            driver.find_element(By.XPATH, "//mat-card[div[text()=PSYCHOLOGIST_NAME]]")
            bot.send_message(CHAT_ID, f"Слот появился!")
            break
        except:
            driver.refresh()

        break

    driver.quit()


if __name__ == "__main__":
    main()
