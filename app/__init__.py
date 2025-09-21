from __future__ import annotations

import importlib.metadata

from dotenv import load_dotenv

load_dotenv()

VERSION = importlib.metadata.version("futlog-backend")
