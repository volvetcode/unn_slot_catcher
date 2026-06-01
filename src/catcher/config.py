from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    login: str
    password: str
    telegram_token: str
    chat_id: str

@lru_cache 
def get_settings() -> Settings:
    return Settings()