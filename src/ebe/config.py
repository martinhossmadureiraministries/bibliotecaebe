"""Carregamento da configuração do sistema (config.yaml + env vars)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class GeminiCfg:
    api_key: str = ""
    modelo_geracao: str = "gemini-2.0-flash"
    modelo_embeddings: str = "text-embedding-004"
    timeout_segundos: int = 120
    rpm: int = 5
    tpm: int = 500_000
    rpd: int = 1_000
    usar_context_caching: bool = True
    cache_ttl_segundos: int = 3600


@dataclass
class PathsCfg:
    curriculum_ativo: str = "state/curriculum.json"
    registry: str = "state/registry.jsonl"
    output_dir: str = "output"
    logs_dir: str = "state/logs"
    hashes_dir: str = "state/hashes"
    embeddings_dir: str = "state/embeddings"
    cache_dir: str = "state/cache"
    prompts_dir: str = "src/ebe/ai/prompts"
    assets_dir: str = "assets"

    def resolve(self, rel: str) -> Path:
        return REPO_ROOT / rel


@dataclass
class EditorialCfg:
    fonte_titulo: str = "Garamond"
    fonte_corpo: str = "Garamond"
    cor_primaria: str = "#1B3A5C"
    cor_secundaria: str = "#2E7D4F"
    cor_terciaria: str = "#C9A14B"
    margens_cm: dict = field(default_factory=lambda: {
        "topo": 2.5, "fundo": 2.5, "esquerda": 3.0, "direita": 2.5,
    })


@dataclass
class GeralCfg:
    sistema_versao: str = "0.1.0"
    lingua: str = "pt-PT"
    versao_biblica: str = "ARC"
    pagina_min: int = 15
    pagina_max: int = 20
    apostilas_por_dia: int = 11
    max_tentativas_geracao: int = 3
    max_tentativas_originalidade: int = 3
    limiar_similaridade: float = 0.70
    limiar_similaridade_estrutura: float = 0.78


@dataclass
class GithubCfg:
    workflow_branch: str = "main"
    auto_commit: bool = True
    auto_push: bool = True


@dataclass
class MapEntry:
    code: str
    json: str
    pdf: str = ""
    status: str = "active"
    first_id: int = 1
    last_id: int = 0
    total: int = 0


@dataclass
class CurriculumCfg:
    active_map: str = "EBE-PLAN-APO-1"
    maps: list[MapEntry] = field(default_factory=list)


@dataclass
class Config:
    geral: GeralCfg = field(default_factory=GeralCfg)
    gemini: GeminiCfg = field(default_factory=GeminiCfg)
    caminhos: PathsCfg = field(default_factory=PathsCfg)
    editorial: EditorialCfg = field(default_factory=EditorialCfg)
    github: GithubCfg = field(default_factory=GithubCfg)
    curriculum: CurriculumCfg = field(default_factory=CurriculumCfg)

    def repo_path(self, rel: str) -> Path:
        return REPO_ROOT / rel


def load_config(path: str | None = None) -> Config:
    """Carrega configuração a partir de config.yaml (se existir) e sobrescreve com env vars."""
    cfg = Config()

    if yaml is None:
        # Sem PyYAML, mantém defaults.
        pass
    else:
        candidates = [Path(path)] if path else [REPO_ROOT / "config.yaml", REPO_ROOT / "config.example.yaml"]
        for p in candidates:
            if p and p.exists():
                with p.open("r", encoding="utf-8") as f:
                    data: Any = yaml.safe_load(f) or {}
                _apply_dict(cfg, data)
                break

    # ---- Sobrescrita por variáveis de ambiente ----
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key:
        cfg.gemini.api_key = env_key

    env_model = os.environ.get("GEMINI_MODEL", "").strip()
    if env_model:
        cfg.gemini.modelo_geracao = env_model

    env_branch = os.environ.get("GITHUB_BRANCH", "").strip()
    if env_branch:
        cfg.github.workflow_branch = env_branch

    # Fallback: garantir curriculum APO-1 se não existir entrada
    if not cfg.curriculum.maps:
        cfg.curriculum.maps = [
            MapEntry(
                code="EBE-PLAN-APO-1",
                json="state/curriculum.json",
                pdf="EBE_Mapa_Completo_Apostilas-2.pdf",
                status="active",
                first_id=1,
                last_id=1029,
                total=1029,
            )
        ]
    return cfg


def _apply_dict(cfg: Config, data: dict) -> None:
    """Aplica um dicionário (YAML) às dataclasses de configuração."""
    def _to(cls: type, section: dict):
        return cls(**{k: v for k, v in section.items() if k in cls.__dataclass_fields__})

    if "geral" in data and isinstance(data["geral"], dict):
        cfg.geral = _to(GeralCfg, {**cfg.geral.__dict__, **data["geral"]})
    if "gemini" in data and isinstance(data["gemini"], dict):
        merged = {**cfg.gemini.__dict__, **data["gemini"]}
        # api_key vem de environment, não do yaml
        merged.pop("api_key", None)
        cfg.gemini = _to(GeminiCfg, merged)
    if "caminhos" in data and isinstance(data["caminhos"], dict):
        cfg.caminhos = _to(PathsCfg, {**cfg.caminhos.__dict__, **data["caminhos"]})
    if "editorial" in data and isinstance(data["editorial"], dict):
        mg = {**cfg.editorial.__dict__, **data["editorial"]}
        if isinstance(mg.get("margens_cm"), dict):
            mg["margens_cm"] = {**cfg.editorial.margens_cm, **mg["margens_cm"]}
        cfg.editorial = _to(EditorialCfg, mg)
    if "github" in data and isinstance(data["github"], dict):
        cfg.github = _to(GithubCfg, {**cfg.github.__dict__, **data["github"]})
    if "curriculum" in data and isinstance(data["curriculum"], dict):
        cc = data["curriculum"]
        cfg.curriculum.active_map = cc.get("active_map", cfg.curriculum.active_map)
        if "maps" in cc and isinstance(cc["maps"], list):
            cfg.curriculum.maps = [MapEntry(**{k: v for k, v in m.items()
                                              if k in MapEntry.__dataclass_fields__})
                                   for m in cc["maps"]]
