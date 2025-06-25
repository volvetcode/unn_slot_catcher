import os

from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://psys.unn.ru/home"
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHROMEDRIVER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../drivers/chromedriver")
)
LOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../logs/catcher.log")
)
PSYCHOLOGISTS = [
    "Подшибихина Светлана Викторовна",
    "Галстян Полина Амаяковна",
    "Баринова Ольга Алексеевна",
    "Курзюкова Юлия Фёдоровна",
]
MESSAGE_TEMPLATE = "{psy} is {plan} to work next week\n"
PSYCHOLOGIST_NAME = os.getenv("PSYCHOLOGIST_NAME")
