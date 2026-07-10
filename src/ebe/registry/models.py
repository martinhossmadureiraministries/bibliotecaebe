"""Modelos do registry (entrada por apostila)."""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RegistryEntry:
    id: int
    numero: str
    codigo: str
    titulo: str
    nivel: str
    instituto: str
    escola: str
    curso: str
    modulo: str
    carga_horaria: str = ""
    status: str = "pending"        # pending | generating | generated | validated | failed | regenerated
    data_geracao: Optional[str] = None
    versao_sistema: str = "0.1.0"
    commit: str = ""
    modelo_gemini: str = ""
    prompt_hash: str = ""
    hash_arquivo: str = ""
    paginas_estimadas: int = 0
    similarity_max: float = 0.0
    retries: int = 0
    caminho_docx: str = ""
    erro: Optional[str] = None
    map_code: str = "EBE-PLAN-APO-1"

    @classmethod
    def pending_from_apostila(cls, a, versao_sistema: str = "0.1.0",
                              map_code: str = "EBE-PLAN-APO-1") -> "RegistryEntry":
        return cls(
            id=a.id, numero=a.numero, codigo=a.codigo, titulo=a.titulo,
            nivel=a.nivel, instituto=a.instituto, escola=a.escola,
            curso=a.curso, modulo=a.modulo, carga_horaria=a.carga_horaria,
            status="pending", versao_sistema=versao_sistema, map_code=map_code,
        )

    def to_json(self) -> dict:
        return asdict(self)

    def mark_generating(self, commit: str = "") -> None:
        self.status = "generating"
        if commit:
            self.commit = commit

    def mark_finalized(self, caminho: str, hash_arquivo: str,
                       paginas: int, modelo: str, prompt_hash: str,
                       similarity: float, retries: int, commit: str) -> None:
        self.status = "generated"
        self.caminho_docx = caminho
        self.hash_arquivo = hash_arquivo
        self.paginas_estimadas = paginas
        self.modelo_gemini = modelo
        self.prompt_hash = prompt_hash
        self.similarity_max = similarity
        self.retries = retries
        self.commit = commit
        self.data_geracao = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def mark_failed(self, erro: str) -> None:
        self.status = "failed"
        self.erro = erro
        self.data_geracao = datetime.now(timezone.utc).isoformat(timespec="seconds")
