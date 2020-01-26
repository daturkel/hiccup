import coloredlogs
import logging
import logging.config
import sys

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "console_formatter": {
            "()": "coloredlogs.ColoredFormatter",
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%I:%M:%S%p",
        }
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "console_formatter",
            "stream": sys.stdout,
        }
    },
    "loggers": {"": {"level": "INFO", "handlers": ["console_handler"]}},
}


def setup_logger(level=logging.INFO):
    logging.config.dictConfig(LOGGING_CONFIG)
