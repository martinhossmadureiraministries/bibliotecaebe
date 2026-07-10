"""Utilitários de sistema de ficheiros."""
from __future__ import annotations

from pathlib import Path
from typing import Callable


def ensure_dir(p: str | Path) -> Path:
    pp = Path(p)
    pp.mkdir(parents=True, exist_ok=True)
    return pp


def safe_slug(s: str, max_len: int = 80) -> str:
    from slugify import slugify
    return slugify(s)[:max_len]


def output_path_for(base_dir: str | Path, apostila) -> Path:
    """Caminho canónico para o DOCX de uma apostila, dentro de base_dir."""
    from slugify import slugify
    base = Path(base_dir)
    pasta = base / f"N{apostila.nivel_id:02d}" / f"I{apostila.instituto_id:02d}" / slugify(apostila.escola) / slugify(apostila.curso)
    pasta.mkdir(parents=True, exist_ok=True)
    fname = f"{apostila.codigo}_{slugify(apostila.titulo)}.docx"
    return pasta / fname
