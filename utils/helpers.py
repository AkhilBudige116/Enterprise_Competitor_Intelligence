"""Utility functions for string formatting, JSON extraction, and company ticker mapping."""
import json
import re
from typing import Any, Optional, Dict
from datetime import datetime, timezone

COMMON_TICKERS = {
    "nvidia": "NVDA",
    "amd": "AMD",
    "intel": "INTC",
    "apple": "AAPL",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "meta": "META",
    "tesla": "TSLA",
    "tsmc": "TSM",
    "qualcomm": "QCOM",
    "broadcom": "AVGO",
    "arm": "ARM",
    "byd": "BYDDF",
    "rivian": "RIVN",
}

def resolve_ticker(company_name: str) -> Optional[str]:
    """Look up a stock ticker symbol for a given company name."""
    clean = re.sub(r"[^a-zA-Z0-9\s]", "", company_name).strip().lower()
    if clean in COMMON_TICKERS:
        return COMMON_TICKERS[clean]
    for name, ticker in COMMON_TICKERS.items():
        if name in clean:
            return ticker
    # If the input itself is a short uppercase ticker (e.g. "NVDA")
    if len(company_name.strip()) <= 5 and company_name.strip().isalpha():
        return company_name.strip().upper()
    return None

def safe_json_parse(text: str) -> Optional[Any]:
    """Robustly extract and parse JSON from model output or raw text."""
    if not text:
        return None
    # 1. Try direct parse
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    
    # 2. Try markdown fenced code block ```json ... ```
    json_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if json_block:
        try:
            return json.loads(json_block.group(1).strip())
        except Exception:
            pass
            
    # 3. Try finding outermost { ... } or [ ... ]
    bracket_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if bracket_match:
        try:
            return json.loads(bracket_match.group(1).strip())
        except Exception:
            pass
            
    return None

def sanitize_filename(name: str) -> str:
    """Sanitize strings for safe filesystem file names."""
    clean = re.sub(r'[\\/*?:"<>| ]', "_", name)
    return clean.strip("_")[:64]

def clean_markdown(md_text: str) -> str:
    """Clean markdown markup for plain text representation."""
    if not md_text:
        return ""
    # Remove markdown headers
    text = re.sub(r"#+\s*", "", md_text)
    # Remove bold/italic markers
    text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)
    # Remove links [text](url) -> text (url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.strip()

def current_timestamp_iso() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
