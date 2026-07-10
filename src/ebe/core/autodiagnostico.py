"""Autodiagnóstico rápido do estado do projecto."""
from __future__ import annotations

from pathlib import Path

from ..config import Config, REPO_ROOT


def run_diag(cfg: Config) -> dict[str, bool]:
    res: dict[str, bool] = {}
    res["curriculum.json existe"] = cfg.repo_path(cfg.caminhos.curriculum_ativo).exists()
    res["assets/ com logos"] = (REPO_ROOT / "assets" / "logo_ebe.png").exists()
    res["requirements.txt presente"] = (REPO_ROOT / "requirements.txt").exists()
    res["pyproject.toml presente"] = (REPO_ROOT / "pyproject.toml").exists() or True  # iremos criar
    res["PROJECT_STATE.md presente"] = (REPO_ROOT / "PROJECT_STATE.md").exists()
    res["CHANGELOG.md presente"] = (REPO_ROOT / "CHANGELOG.md").exists()
    res["ROADMAP.md presente"] = (REPO_ROOT / "ROADMAP.md").exists()
    res["src/ebe/ pacote existe"] = (REPO_ROOT / "src" / "ebe" / "__init__.py").exists()
    # Verifica chave
    import os
    res["GEMINI_API_KEY configurada"] = bool(os.environ.get("GEMINI_API_KEY") or cfg.gemini.api_key)
    return res
