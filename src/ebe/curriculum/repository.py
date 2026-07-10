"""Repositório do currículo (fonte de verdade canónica: state/curriculum.json)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

from ..config import Config
from ..exceptions import CurriculumError
from .models import ApostilaInfo
from .validator import validate_or_raise


class CurriculumRepository:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._data: Optional[dict] = None

    @property
    def data(self) -> dict:
        if self._data is None:
            self._load()
        assert self._data is not None
        return self._data

    def _load(self) -> None:
        # Localiza o mapa activo
        active_code = self.cfg.curriculum.active_map
        entry = next((m for m in self.cfg.curriculum.maps if m.code == active_code), None)
        if entry is None:
            raise CurriculumError(f"Mapa activo '{active_code}' não encontrado em config.yaml")
        p = self.cfg.repo_path(entry.json)
        if not p.exists():
            raise CurriculumError(f"Ficheiro de currículo não encontrado: {p}")
        with p.open("r", encoding="utf-8") as f:
            self._data = json.load(f)
        validate_or_raise(self._data, expected_total=entry.total or 1029)

    def all(self) -> list[ApostilaInfo]:
        return [ApostilaInfo.from_dict(a) for a in self.data["apostilas"]]

    def get_by_id(self, id_: int) -> Optional[ApostilaInfo]:
        for a in self.data["apostilas"]:
            if a.get("id") == id_:
                return ApostilaInfo.from_dict(a)
        return None

    def pending(self, done_ids: Iterable[int], n: int = 11) -> list[ApostilaInfo]:
        done = set(done_ids)
        out = []
        for a in self.data["apostilas"]:
            if a["id"] in done:
                continue
            out.append(ApostilaInfo.from_dict(a))
            if len(out) >= n:
                break
        return out

    def next_pending(self, done_ids: Iterable[int], n: int = 11) -> list[ApostilaInfo]:
        return self.pending(done_ids, n=n)
