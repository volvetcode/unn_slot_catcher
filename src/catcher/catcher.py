import logging
from datetime import datetime, timedelta
from functools import wraps
from time import sleep
from types import TracebackType
from typing import Any
from zoneinfo import ZoneInfo

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from catcher.browser import create_driver
from catcher.config import Settings, get_settings
from catcher.logging_config import configure_logging
from catcher.notifier import Notifier, TelegramNotifier

MOSCOW_TZ = ZoneInfo('Europe/Moscow')


class Catcher:
    def __init__(
        self,
        settings: Settings | None = None,
        notifier: Notifier | None = None,
    ):
        configure_logging()
        logging.info('Logging configured')

        try:
            logging.info('Loading settings')
            self.settings = settings or get_settings()
        except Exception as e:
            logging.error('Failed to log setting')
            raise RuntimeError("Couldn't load settings. Check your .env file") from e

        logging.info('setting up...')
        self.driver = create_driver(self.settings)
        self.notifier = notifier or TelegramNotifier(
            token=self.settings.telegram_token,
            chat_id=self.settings.chat_id,
        )
        logging.info('finished setting up')

    def __enter__(self) -> 'Catcher':
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        logging.info('quitting')
        self.driver.quit()

    @staticmethod
    def retry(func: Any) -> Any:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            name = func.__name__.strip('_').title()
            for attempt in range(1, self.settings.retries + 1):
                try:
                    result = func(self, *args, **kwargs)
                    logging.info(f'{name} succeeded on attempt №{attempt}')
                    return result
                except (NoSuchElementException, TimeoutException):
                    logging.warning(f'{name} failed. Attempt №{attempt}')
                    sleep(self.settings.retry_delay)

            raise Exception(f'{func.__name__} failed after all retries')

        return wrapper

    @retry
    def _login(self) -> None:
        """Authenticate user."""
        wait = WebDriverWait(self.driver, self.settings.time_to_wait)
        self.driver.get(str(self.settings.base_url))

        sleep(self.settings.action_delay)
        login_input = wait.until(
            EC.visibility_of_element_located((By.ID, 'mat-input-0'))
        )
        login_input.send_keys(self.settings.login)

        sleep(self.settings.action_delay)
        password_input = wait.until(
            EC.visibility_of_element_located((By.ID, 'mat-input-1'))
        )
        password_input.send_keys(self.settings.password)

        sleep(self.settings.action_delay)
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='ВОЙТИ']]"))
        )
        login_button.click()

        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//h1[contains(text(), 'Форма записи на приём к психологу')]",
                )
            )
        )

    def _refresh(self) -> None:
        self.driver.refresh()
        logging.info('Refreshed the schedule')

    @retry
    def _next_page(self) -> None:
        """Go to next page in calendar"""
        wait = WebDriverWait(self.driver, self.settings.time_to_wait)
        next_week_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'week-next'))
        )
        logging.info('Opened the next week page')
        next_week_button.click()

    def _open_schedule_page(self) -> None:
        try:
            self._refresh()
            self._next_page()
        except Exception:
            logging.error("Couldn't go to the next page")
            try:
                self._login()
            except Exception:
                logging.error("Couldn't login")

    def _search_for_a_slot(self, psychologist: str) -> bool:
        """Searches for a slot from a particular psychologist"""
        logging.info(f'searching for {psychologist}')
        result = False
        try:
            wait = WebDriverWait(self.driver, self.settings.time_to_wait)
            psychologist_slot = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//div[normalize-space(text())='{psychologist}']")
                )
            )
            # TODO: teach the bot to book slots
            psychologist_slot.click()
            logging.info(f'found {psychologist}')
            result = True
        except TimeoutException:
            # No available slot is the expected/default state.
            pass
        except Exception as e:
            logging.error(
                f'Unexpected error searching for {psychologist}: {e}', exc_info=True
            )
        return result

    def _send_report(self, psychologist: str, found_slot: bool) -> None:
        if found_slot:
            found_at = datetime.now(MOSCOW_TZ).strftime('%H:%M:%S')
            message = f'{psychologist} открыла слот в {found_at}. Бегом записываться!'
        else:
            message = f'{psychologist} не открыла слот'
            logging.warning("couldn't find a psychologist")

        self.notifier.send(message)

    def monitor(self) -> None:
        """Main monitoring loop."""

        psychologist = self.settings.psychologists[0]
        time_start = datetime.now(MOSCOW_TZ)
        target_time = time_start + timedelta(hours=self.settings.duration_hours)

        self._login()
        found_slot = False
        while datetime.now(MOSCOW_TZ) < target_time:
            self._open_schedule_page()
            found_slot = self._search_for_a_slot(psychologist)

            if found_slot:
                break

        self._send_report(psychologist, found_slot)

        total_time = datetime.now(MOSCOW_TZ) - time_start
        total_minutes = total_time.total_seconds() / 60
        logging.info(
            f'Statistics: runtime={total_minutes:.1f}mins, '
            f'slot_found={found_slot} for {psychologist}'
        )
