import logging
import os
import sys
from logging import config
from logging.handlers import RotatingFileHandler
from typing import Any

from .settings import settings


def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

create_directory(os.path.join(settings.BASE_DIR, "logs"))

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DEFAULT_HANDLERS = [
    "console",
]
LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": LOG_FORMAT},
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": (
                "%(levelprefix)s %(client_addr)s - '%(request_line)s' "
                "%(status_code)s"
            ),
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": LOG_DEFAULT_HANDLERS,
            "level": "INFO",
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "formatter": "verbose",
        "handlers": LOG_DEFAULT_HANDLERS,
    },
}

config.dictConfig(config=LOGGING)
logger = logging.getLogger("mark")

logger.setLevel(settings.LOG_LEVEL)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
file_handler = RotatingFileHandler(
    os.path.join(settings.BASE_DIR, "logs", "log.log"),
    maxBytes=500000,
    backupCount=3,
    encoding="utf-8",
)
logger.addHandler(file_handler)