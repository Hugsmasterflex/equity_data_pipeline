import json
import logging
import logging.config
import os
import re
from pathlib import Path
from pythonjsonlogger import jsonlogger
from ingestion.log_context import get_context


def configure_logging(app_name: str = "app", log_dir: str | Path = "logs") -> None:
    """
    Configure logging once per process.
    Env vars:
      LOG_LEVEL=INFO|DEBUG|WARNING
      LOG_FORMAT=console|json
      ENV=local|dev|prod  (controls file handler)
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt = os.getenv("LOG_FORMAT", "console").lower()
    env = os.getenv("ENV", "local").lower()

    handlers = ["console"]
    handler_defs = {
        "console": {
            "class": "logging.StreamHandler",
            "level": level,
            "stream": "ext://sys.stdout",
            "filters": ["context", "redact"],
            "formatter": "console" if fmt == "console" else "json",
        }
    }

    # Local: also write a rotating file for persistence
    if env == "local":
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        handlers.append("file")
        handler_defs["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "filename": str(Path(log_dir) / f"{app_name}.log"),
            "maxBytes": 10_000_000,   # 10 MB
            "backupCount": 10,
            "encoding": "utf-8",
            "filters": ["context", "redact"],
            "formatter": "console" if fmt == "console" else "json",
        }

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "context": {"()": ContextFilter},
            "redact": {"()": RedactFilter},
        },
        "formatters": {
            "console": {"()": ConsoleFormatter},
            "json": {"()": JSONFormatter},
        },
        "handlers": handler_defs,
        "loggers": {
            # root logger
            "": {"level": level, "handlers": handlers},
            # quiet noisy libs a bit
            "botocore": {"level": "WARNING"},
            "boto3": {"level": "WARNING"},
            "urllib3": {"level": "WARNING"},
            "s3fs": {"level": "WARNING"},
            "asyncio": {"level": "WARNING"},
        },
    }

    logging.config.dictConfig(config)