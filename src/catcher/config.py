from datetime import datetime
from pathlib import Path

from pydantic import Field

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_log_path() -> str:
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return str(Path('logs') / f'log-{timestamp}.json')


class Settings(BaseSettings):  # type: ignore[misc]
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    # credentials
    login: str
    password: str

    # notifier config
    telegram_token: str
    chat_id: str

    # browser config
    is_prod: bool
    chromedriver_path: str
    time_to_wait: int

    # catcher behaviour
    duration_hours: int
    action_delay: int
    retries: int
    retry_delay: int

    # app constants
    base_url: str
    psychologists: list[str]
    log_path: str = Field(default_factory=default_log_path)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
