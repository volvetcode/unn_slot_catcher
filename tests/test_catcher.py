import pytest
import subprocess
from selenium.webdriver.common.by import By

from src.catcher.catcher import Catcher
import src.catcher.constants as const

# they are pretty slow. i think i should use them
# only once i want to push to prod

# tests are supposed to be running from src

@pytest.fixture
def bot():
    bot = Catcher(teardown=True)
    yield bot
    bot.quit()

def test_catcher_init_real(bot):
    assert bot is not None

def test_no_driver(bot):
    subprocess.run(["mv", "../drivers/chromedriver", "../"])
    assert True


def test_login(bot):
    bot.login()
    header = bot.find_element(
        By.XPATH,
        "//h1[contains(text(), 'Форма записи на приём к психологу')]"
    )
    assert header is not None

subprocess.run(["mv", "drivers/chromedriver", "../"])