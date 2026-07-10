"""Configuração centralizada da aplicação."""

import os
from pathlib import Path
from typing import Optional

# Raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Diretórios principais
SRC_DIR = PROJECT_ROOT / "src"
STATE_DIR = PROJECT_ROOT / "state"
OUTPUT_DIR = PROJECT_ROOT / "output"
DOCS_DIR = PROJECT_ROOT / "docs"
ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_EBE_DIR = PROJECT_ROOT / "_assets"
LOGO_DIR = ASSETS_EBE_DIR

# Arquivos de estado
CURRICULUM_JSON = STATE_DIR / "curriculum.json"
REGISTRY_JSONL = STATE_DIR / "registry.jsonl"
LAST_ERROR_JSON = STATE_DIR / "last_error.json"

# Configurações
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LANG = os.getenv("LANG", "pt_PT")  # Português europeu por defeito
BIBLE_VERSION = "ARC"  # Almeida Revista e Corrigida

# API Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-pro-002"
GEMINI_TIMEOUT = 60
RATE_LIMIT_RPM = 50  # Requisições por minuto (tier gratuito)

# Limites de produção
APOSTILAS_POR_DIA = 11
MAX_TENTATIVAS_REGENERACAO = 3
LIMIAR_SIMILARIDADE_ORIGINALIDADE = 0.75

# Paths dos modelos
LOGO_EBE = LOGO_DIR / "logo_ebe.png"
LOGO_PEQUENO = LOGO_DIR / "logo_pequeno.png"
LOGO_EMBLEMA = LOGO_DIR / "logo_emblema.png"
LOGO_MARCA_DAGUA = LOGO_DIR / "logo_marca_dagua.png"

# Cores institucionais
COR_PRIMARIA = "#1B3A5C"  # azul-marinho
COR_SECUNDARIA = "#2E7D4F"  # verde
COR_TERCIARIA = "#C9A14B"  # dourado

# Tipografia
FONTE_TITULO = "Garamond"
FONTE_CORPO = "Garamond"
FONTE_MONO = "Consolas"


def ensure_dirs():
    """Garante que todos os diretórios essenciais existem."""
    for d in [STATE_DIR, OUTPUT_DIR, DOCS_DIR, ASSETS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """Obtém configuração por chave (prioritário: env vars > defaults)."""
    globals_map = {
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "GEMINI_MODEL": GEMINI_MODEL,
        "DEBUG": DEBUG,
    }
    return globals_map.get(key, default)
