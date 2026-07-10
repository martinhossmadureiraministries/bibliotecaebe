"""Modelos de dados do currículo (Nível → Instituto → Escola → Curso → Módulo → Apostila)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ApostilaInfo:
    id: int
    numero: str
    titulo: str
    modulo_id: int
    curso_id: str
    escola_id: str
    instituto_id: int
    nivel_id: int
    nivel: str
    instituto: str
    escola: str
    curso: str
    modulo: str
    carga_horaria: str = ""
    caminho: list[str] = field(default_factory=list)

    @property
    def codigo(self) -> str:
        return f"EBE-APO-{self.numero}"

    @property
    def slug(self) -> str:
        from slugify import slugify
        return slugify(f"EBE-APO-{self.numero}_{self.titulo}")

    @classmethod
    def from_dict(cls, d: dict) -> "ApostilaInfo":
        return cls(
            id=d["id"],
            numero=d["numero"],
            titulo=d["titulo"],
            modulo_id=d["modulo_id"],
            curso_id=d["curso_id"],
            escola_id=d["escola_id"],
            instituto_id=d["instituto_id"],
            nivel_id=d["nivel_id"],
            nivel=d.get("nivel", ""),
            instituto=d.get("instituto", ""),
            escola=d.get("escola", ""),
            curso=d.get("curso", ""),
            modulo=d.get("modulo", ""),
            carga_horaria=d.get("carga_horaria", ""),
            caminho=d.get("caminho", []),
        )
