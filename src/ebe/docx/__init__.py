"""Módulo de geração de documentos Word (.docx)."""

from .styles import (
    COR_PRIMARIA,
    COR_SECUNDARIA,
    COR_TERCIARIA,
    FONTE_TITULO,
    FONTE_CORPO,
    configurar_estilos_base,
    add_capa,
    add_marco_filosofico,
    novo_documento,
)

__all__ = [
    "COR_PRIMARIA",
    "COR_SECUNDARIA",
    "COR_TERCIARIA",
    "FONTE_TITULO",
    "FONTE_CORPO",
    "configurar_estilos_base",
    "add_capa",
    "add_marco_filosofico",
    "novo_documento",
]
