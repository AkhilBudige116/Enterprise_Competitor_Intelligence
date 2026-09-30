"""Sanitized structured logging."""
import logging
import re
import sys
from typing import Optional

SECRET_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z-_]{35}"),               # Google API key
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),                 # OpenAI API key
    re.compile(r"tvly-[a-zA-Z0-9-_]{20,}"),             # Tavily API key
    re.compile(r"gsk_[a-zA-Z0-9]{20,}"),                # Groq API key
    re.compile(r"(api[_-]?key[\s:=]+)['\"]?([^'\"\s]{8,})['\"]?", re.IGNORECASE),
]

class SanitizedFormatter(logging.Formatter):
    """Masks API keys and secrets in log messages."""
    def format(self, record: logging.LogRecord) -> str:
        orig = super().format(record)
        sanitized = orig
        for pattern in SECRET_PATTERNS:
            if pattern.groups > 0:
                sanitized = pattern.sub(r"\1[REDACTED_KEY]", sanitized)
            else:
                sanitized = pattern.sub("[REDACTED_KEY]", sanitized)
        return sanitized

def get_logger(name: str = "EnterpriseCI", level: Optional[str] = None) -> logging.Logger:
    """Creates a configured, secret-safe logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = SanitizedFormatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)
    logger.setLevel(log_level)
    return logger
