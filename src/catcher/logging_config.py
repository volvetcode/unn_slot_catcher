import logging
import sys
from catcher.config import Settings


def configure_logging(settings: Settings) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(settings.log_path, mode='w')
    file_handler.setFormatter(
        logging.Formatter('"%(asctime)s","%(levelname)s","%(message)s"')
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        logging.Formatter('"%(asctime)s","%(levelname)s","%(message)s"')
    )

    logger.handlers = [file_handler, stream_handler]
