import json
import logging

from datetime import datetime
from pathlib import Path



class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            'timestamp': self.formatTime(record, datefmt='%Y-%m-%dT%H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
        }

        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)


def configure_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_path = str(Path('logs') / f'log-{timestamp}.json')

    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_handler.setFormatter(JsonFormatter())

    logger.handlers = [file_handler]
