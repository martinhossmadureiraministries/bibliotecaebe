"""Gestão do CachedContent do Gemini."""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

from ..config import Config

log = logging.getLogger("ebe.cache")


class ContextCache:
    """Guarda referência ao cached content (nome + TTL) em disco, para reutilizar
    entre execuções do mesmo dia."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.path = cfg.repo_path(cfg.caminhos.cache_dir) / "gemini_cache.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def get_active(self) -> Optional[str]:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if data.get("expires_at", 0) > time.time():
                return data.get("name")
        except Exception:
            pass
        return None

    def save(self, name: str, ttl_seconds: int) -> None:
        data = {"name": name, "expires_at": time.time() + ttl_seconds - 60}
        self.path.write_text(json.dumps(data), encoding="utf-8")
