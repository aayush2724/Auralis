"""
conftest.py
──────────────────────────────────────────────────────────────────
Pytest configuration: load .env before any tests run so that
GEMINI_API_KEY and DATABASE_URL are available to the application code.
"""
from __future__ import annotations

import os
from pathlib import Path

# Load the .env file from the project root (two levels up from server/tests/)
_dotenv_path = Path(__file__).parent.parent.parent / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_dotenv_path, override=False)
except ImportError:
    pass  # python-dotenv not installed; rely on env vars being set externally
