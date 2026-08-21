from functools import cache

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    base_url: HttpUrl
    psychologists: list[str]


@cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
