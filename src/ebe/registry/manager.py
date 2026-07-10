"""Gestor do ficheiro registry.jsonl — leitura, escrita atómica, updates."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Iterable, Optional

from ..config import Config
from ..curriculum.models import ApostilaInfo
from .models import RegistryEntry


class RegistryManager:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.path = cfg.repo_path(cfg.caminhos.registry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict[int, RegistryEntry] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        self._cache.clear()
        if not self.path.exists():
            self._loaded = True
            return
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    entry = RegistryEntry(**d)
                    self._cache[entry.id] = entry
                except Exception:
                    # Linha corrompida: ignoramos, não derruba o sistema
                    continue
        self._loaded = True

    def _append_atomic(self, entry: RegistryEntry) -> None:
        """Escreve a entrada nova com append, mas primeiro confirma que o ID
        não foi escrito desde o cache (evita duplicação)."""
        # Reescreve o ficheiro inteiro é mais seguro mas mais caro; optamos por
        # append + verificação de cache, e um comando `repair` para consolidar.
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_json(), ensure_ascii=False) + "\n")
        self._cache[entry.id] = entry

    def get(self, id_: int) -> Optional[RegistryEntry]:
        self._load()
        return self._cache.get(id_)

    def all(self) -> list[RegistryEntry]:
        self._load()
        return [self._cache[k] for k in sorted(self._cache)]

    def done_ids(self) -> set[int]:
        self._load()
        return {i for i, e in self._cache.items() if e.status in {"generated", "validated"}}

    def failed_ids(self) -> set[int]:
        self._load()
        return {i for i, e in self._cache.items() if e.status == "failed"}

    def pending_generating_ids(self) -> set[int]:
        self._load()
        return {i for i, e in self._cache.items() if e.status in {"pending", "generating"}}

    def ensure_pending(self, apostila: ApostilaInfo) -> RegistryEntry:
        """Garante que existe uma entrada pending para a apostila; devolve-a."""
        self._load()
        if apostila.id in self._cache:
            return self._cache[apostila.id]
        entry = RegistryEntry.pending_from_apostila(
            apostila,
            versao_sistema=self.cfg.geral.sistema_versao,
            map_code=self.cfg.curriculum.active_map,
        )
        # Como é novo, usamos append atómico
        self._append_atomic(entry)
        return entry

    def update(self, entry: RegistryEntry) -> None:
        """Actualiza uma entrada. Como o ficheiro é JSONL, marcamos a entrada
        antiga como obsoleta reescrevendo o ficheiro inteiro de forma atómica."""
        self._load()
        self._cache[entry.id] = entry
        self._rewrite_atomic()

    def _rewrite_atomic(self) -> None:
        # Reescrever em tmp e renomear
        tmp_fd, tmp_name = tempfile.mkstemp(prefix=".registry.", suffix=".tmp",
                                            dir=str(self.path.parent))
        try:
            with open(tmp_fd, "w", encoding="utf-8") as f:
                for e in self.all():
                    f.write(json.dumps(e.to_json(), ensure_ascii=False) + "\n")
            Path(tmp_name).replace(self.path)
        except Exception:
            Path(tmp_name).unlink(missing_ok=True)
            raise
