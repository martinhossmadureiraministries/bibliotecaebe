"""Verificação de originalidade via embeddings (similaridade de cosseno)."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

import numpy as np

from ..config import Config
from ..exceptions import OriginalityError
from .gemini_client import GeminiClient

log = logging.getLogger("ebe.originality")


def cosine(a: list[float], b: list[float]) -> float:
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    na = np.linalg.norm(va)
    nb = np.linalg.norm(vb)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(va, vb) / (na * nb))


class OriginalityChecker:
    """Compara texto novo com o histórico de apostilas para detectar similaridade."""

    def __init__(self, cfg: Config, client: GeminiClient):
        self.cfg = cfg
        self.client = client
        self.dir = cfg.repo_path(cfg.caminhos.embeddings_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, apostila_id: int) -> Path:
        return self.dir / f"EBE-APO-{apostila_id:04d}.npz"

    def store(self, apostila_id: int, texto: str) -> list[float]:
        vec = self.client.embed(texto)
        np.savez_compressed(self._path(apostila_id), vec=np.array(vec, dtype=np.float32))
        return vec

    def load_all(self) -> list[tuple[int, np.ndarray]]:
        out = []
        for f in sorted(self.dir.glob("EBE-APO-*.npz")):
            try:
                aid = int(f.stem.split("-")[-1])
                arr = np.load(f)["vec"]
                out.append((aid, arr))
            except Exception:
                continue
        return out

    def max_similarity(self, texto: str) -> tuple[float, int | None]:
        """Devolve (similaridade máxima, id_da_apostila_mais_próxima)."""
        new_vec = np.array(self.client.embed(texto), dtype=np.float32)
        n_new = np.linalg.norm(new_vec)
        if n_new == 0:
            return 0.0, None
        best = (0.0, None)
        for aid, arr in self.load_all():
            n = np.linalg.norm(arr)
            if n == 0:
                continue
            s = float(np.dot(new_vec, arr) / (n_new * n))
            if s > best[0]:
                best = (s, aid)
        return best

    def assert_original(self, texto: str,
                         limiar: float | None = None,
                         contexto: str = "texto") -> float:
        limiar = limiar if limiar is not None else self.cfg.geral.limiar_similaridade
        score, other = self.max_similarity(texto)
        if other is not None:
            log.info("Similaridade (%s) vs ap. %s: %.3f (limiar %.2f)",
                     contexto, other, score, limiar)
        if score > limiar:
            raise OriginalityError(
                f"Similaridade {score:.3f} acima do limiar {limiar:.2f} vs apostila {other} ({contexto})"
            )
        return score
