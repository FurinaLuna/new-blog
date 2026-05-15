import json
import logging
import sys
from datetime import datetime, timezone

from app.core.config import get_settings
from app.middleware.request_id import request_id_ctx


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        rid = request_id_ctx.get("")
        if rid:
            log_entry["request_id"] = rid
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        rid = request_id_ctx.get("")
        rid_part = f" [{rid}]" if rid else ""
        base = f"{datetime.now(timezone.utc).isoformat()} | {record.levelname:<8} | {record.name}{rid_part} | {record.getMessage()}"
        if record.exc_info and record.exc_info[1]:
            base += "\n" + self.formatException(record.exc_info)
        return base


def setup_logging() -> None:
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)

    if settings.log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(TextFormatter())

    logging.root.handlers = [handler]
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
