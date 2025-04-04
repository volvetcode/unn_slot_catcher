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
    print("Starting the script...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome( \
        options=options, \
        service=service
    )

    print("Logging in...")
    driver.get("https://psys.unn.ru/home")
    driver.find_element(By.ID, "mat-input-0").send_keys(LOGIN)
    driver.find_element(By.ID, "mat-input-1").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[span[text()='ВОЙТИ']]").click()
    bot = TeleBot(token=TELEGRAM_TOKEN)

    print("Looking for a slot...")
    start_time = time.time()
    last_10 = 0
    while True:
        time.sleep(1)
        time_passed = time.time() - start_time
        current = time_passed // 600
        if current > last_10:
            print(f"It's been {current} minutes")
            last_10 = current

        next_week_button = driver.find_element(By.CLASS_NAME, "week-next")
        next_week_button.click()

        time.sleep(1)
        try:
            driver.find_element(By.XPATH, "//mat-card[div[text()='Подшибихина Светлана Викторовна']]")
            print("Slot found!")
            bot.send_message(CHAT_ID, f"Слот появился!")
            break
        except:
            driver.refresh()
        
        if time_passed > 60 * 60 * 6:
            print("It's been 6 hours, stopping the script.")
            bot.send_message(CHAT_ID, f"Слот не появился за 6 часов.")
            break
        
    
    driver.close()
    driver.quit()


if __name__ == "__main__":
    main()
