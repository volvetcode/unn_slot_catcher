"""Notification module for sending messages via different channels."""

from abc import ABC, abstractmethod
from typing import Optional

import requests
from requests import Session

class Notifier(ABC):
    """Protocol for Notifiers that can send messages"""

    @abstractmethod
    def send(self, text: str) -> None:
        """Send a text message through the notifier"""
        pass

class TelegramNotifier(Notifier):
    """Send notifications via Telegram bot."""

    def __init__(
        self,
        token: Optional[str] = None,
        chat_id: Optional[int] = None,
        session: Optional[Session] = None,
        timeout: float = 10.0
    ):
        self.token = token
        self.chat_id = chat_id
        self.session = session or requests.Session()
        self.timeout = timeout

        if not self.token:
            raise ValueError("TELEGRAM_TOKEN is required")

        if not self.chat_id:
            raise ValueError("CHAT_ID is required")

    def send(self, text: str) -> None:
        """Send a message via telegram bot"""

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        params = {
            "chat_id": self.chat_id,
            "text": text
        }

        response = self.session.post(
            url,
            params=params,
            timeout=self.timeout,
        )

        # Raise exceptions for 4xx/5xx status codes
        response.raise_for_status()


