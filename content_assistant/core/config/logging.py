from content_assistant.core.config.settings import get_settings
import logging.config

settings = get_settings()

LOGGING_LEVEL = "DEBUG" if settings.debug else "INFO"

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOGGING_LEVEL,
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console"],
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["console"],
            "level": LOGGING_LEVEL if settings.debug else "WARN",
            "propagate": False,
        },
        "alembic.runtime.migration": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(logging_config)
