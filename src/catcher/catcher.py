import logging
from time import sleep, time
from functools import wraps
from typing import Any
from types import TracebackType

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from catcher.config import Settings
from catcher.browser import create_driver
from catcher.logging_config import configure_logging
from catcher.notifier import Notifier


class Catcher:
    def __init__(
        self,
        settings: Settings,
        notifier: Notifier,
    ):
        self.settings = settings
        configure_logging(self.settings)
        logging.info('setting up...')
        self.driver = create_driver(self.settings)
        self.notifier = notifier
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
    def retry_action(action_name: str) -> Any:
        def decorator(func: Any) -> Any:
            @wraps(func)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                for attempt in range(1, self.settings.retries + 1):
                    try:
                        result = func(self, *args, **kwargs)
                        logging.info(f'{action_name} succeeded on attempt №{attempt}')
                        return result
                    except (NoSuchElementException, TimeoutException):
                        logging.warning(f'{action_name} failed. Attempt №{attempt}')
                        sleep(self.settings.retry_delay)

                raise Exception(f'{action_name} failed after all retries')

            return wrapper

        return decorator

    @retry_action('Login')  # type: ignore[misc]
    def _login(self) -> None:
        """Authenticate user."""
        wait = WebDriverWait(self.driver, self.settings.time_to_wait)
        self.driver.get(self.settings.base_url)

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

    @retry_action('Next page')  # type: ignore[misc]
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
        except (NoSuchElementException, TimeoutException):
            pass
        except Exception as e:
            logging.error(
                f'Unexpected error searching for {psychologist}: {e}', exc_info=True
            )
        return result

    def _send_report(self, psychologist: str, found_slot: bool) -> None:
        if found_slot:
            message = f'{psychologist} открыла слот. Бегом записываться!'
        else:
            message = f'{psychologist} не открыла слот'
            logging.warning("couldn't find a psychologist")

        self.notifier.send(message)

    def monitor(self) -> None:
        """Main monitoring loop."""

        psychologist = self.settings.psychologists[0]
        time_start = time()
        target_time = self.settings.duration_hours * 60 * 60

        self._login()
        found_slot = False
        while (time() - time_start) < target_time:
            self._open_schedule_page()
            found_slot = self._search_for_a_slot(psychologist)

            if found_slot:
                break

        self._send_report(psychologist, found_slot)

        total_time = (time() - time_start) / 60
        logging.info(
            f'Statistics: runtime={total_time:.0f}mins, slot_found={found_slot} for {self.settings.psychologists[0]}'
        )
