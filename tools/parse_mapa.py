"""
Parser do Mapa Curricular PDF (EBE_Mapa_Completo_Apostilas-2.pdf)
=================================================================

Extrai a hierarquia Nível → Instituto → Escola → Curso → Módulo → Apostila
e gera o ficheiro state/curriculum.json como fonte de verdade canónica.

Uso (a partir da raiz do repo):
    python3 tools/parse_mapa.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional

import pdfplumber

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF  = os.path.join(REPO, "EBE_Mapa_Completo_Apostilas-2.pdf")
OUT  = os.path.join(REPO, "state", "curriculum.json")

# --- Regexes --------------------------------------------------------------

RE_NIVEL     = re.compile(r"^NÍVEL\s+(\d+)\s*[—-]\s*(.+)$", re.IGNORECASE)
RE_INSTITUTO = re.compile(r"^Instituto\s+(\d+)\s*[—-]\s*(.+)$", re.IGNORECASE)
RE_ESCOLA    = re.compile(r"^Escola\s+de\s+(.+)$", re.IGNORECASE)
# "Escola ABC da Teologia" e afins — também começam por "Escola" mas não contêm ":"
# Título de curso começa com "Curso:"
RE_CURSO     = re.compile(r"^Curso:\s*(.+?)\s*·\s*Carga horária:\s*(.+)$")
RE_MODULO    = re.compile(r"^Módulo\s+(\d+)\s*[—-]\s*(.+)$")
RE_APOSTILA  = re.compile(r"^(\d{1,4})[\.\)]\s*(.+)$")
RE_FIM       = re.compile(r"^Total de apostilas mapeadas")


@dataclass
class Apostila:
    id: int
    numero: str            # "0001" … "1029"
    titulo: str
    modulo_id: int
    curso_id: str
    escola_id: str
    instituto_id: int
    nivel_id: int
    # nomes
    nivel: str
    instituto: str
    escola: str
    curso: str
    modulo: str
    carga_horaria: str = ""
    caminho: list[str] = field(default_factory=list)  # caminho hierárquico literal


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse() -> dict:
    if not os.path.exists(PDF):
        sys.exit(f"PDF não encontrado: {PDF}")

    # Estado do parser
    nivel: dict = {"id": 0, "nome": ""}
    instituto: dict = {"id": 0, "nome": ""}
    escola_nome: str = ""
    curso: dict = {"id": "", "nome": "", "carga": ""}
    modulo: dict = {"id": 0, "nome": ""}

    apostilas: list[Apostila] = []
    escolas_seen: list[str] = []
    cursos_seen: list[dict] = []
    modulos_seen: list[dict] = []

    # Primeiro percorremos as páginas 5+ (p1=1 idx). Páginas 1-4 são capa/índice.
    with pdfplumber.open(PDF) as pdf:
        for page_idx, page in enumerate(pdf.pages, 1):
            if page_idx < 5:
                continue
            text = page.extract_text() or ""
            lines = [_norm(l) for l in text.split("\n") if l.strip()]
            for line in lines:
                # remover cabeçalho/rodapé
                if line.startswith("Escola Bíblica Epignósis"):
                    continue
                if re.match(r"^EBE-PLAN-APO\s*·\s*\d+$", line):
                    continue
                if RE_FIM.match(line):
                    break

                m = RE_NIVEL.match(line)
                if m:
                    nivel = {"id": int(m.group(1)), "nome": _norm(m.group(2))}
                    instituto = {"id": 0, "nome": ""}
                    escola_nome = ""
                    curso = {"id": "", "nome": "", "carga": ""}
                    modulo = {"id": 0, "nome": ""}
                    continue

                m = RE_INSTITUTO.match(line)
                if m:
                    instituto = {"id": int(m.group(1)), "nome": _norm(m.group(2))}
                    escola_nome = ""
                    curso = {"id": "", "nome": "", "carga": ""}
                    modulo = {"id": 0, "nome": ""}
                    continue

                m = RE_CURSO.match(line)
                if m:
                    curso = {"id": f"C{len(cursos_seen)+1:04d}",
                             "nome": _norm(m.group(1)),
                             "carga": _norm(m.group(2))}
                    cursos_seen.append({**curso,
                                        "escola": escola_nome,
                                        "instituto": instituto["id"],
                                        "nivel": nivel["id"]})
                    modulo = {"id": 0, "nome": ""}
                    continue

                m = RE_MODULO.match(line)
                if m:
                    modulo = {"id": int(m.group(1)), "nome": _norm(m.group(2))}
                    modulos_seen.append({**modulo,
                                         "curso": curso["id"],
                                         "curso_nome": curso["nome"]})
                    continue

                # Escola — só reconhece se já estivermos num Instituto
                # e a linha começa com "Escola" mas NÃO é "Curso:", "Módulo", etc.
                # Evita falso positivo com "Escola Bíblica Epignósis" (já filtrado).
                if instituto["id"] and line.lower().startswith("escola ") and "·" not in line and ":" not in line:
                    # Evita pegar linhas como "Escola Profética (3 cursos)" do índice
                    if re.search(r"\(\d+\s+curso", line):
                        continue
                    escola_nome = re.sub(r"^Escola\s+de\s+", "", line, flags=re.I)
                    escola_nome = re.sub(r"^Escola\s+", "", escola_nome, flags=re.I)
                    escola_nome = _norm(escola_nome)
                    if escola_nome not in escolas_seen:
                        escolas_seen.append(escola_nome)
                    curso = {"id": "", "nome": "", "carga": ""}
                    modulo = {"id": 0, "nome": ""}
                    continue

                m = RE_APOSTILA.match(line)
                if m and curso["id"] and modulo["id"]:
                    num = int(m.group(1))
                    titulo = _norm(m.group(2))
                    # Quebras de pdfplumber por vezes cortam; aceitamos o título como está.
                    apostilas.append(Apostila(
                        id=num,
                        numero=f"{num:04d}",
                        titulo=titulo,
                        modulo_id=modulo["id"],
                        curso_id=curso["id"],
                        escola_id=escola_nome,
                        instituto_id=instituto["id"],
                        nivel_id=nivel["id"],
                        nivel=nivel["nome"],
                        instituto=instituto["nome"],
                        escola=escola_nome,
                        curso=curso["nome"],
                        modulo=modulo["nome"],
                        carga_horaria=curso["carga"],
                        caminho=[nivel["nome"], instituto["nome"], escola_nome,
                                 curso["nome"], f"Módulo {modulo['id']} — {modulo['nome']}",
                                 titulo],
                    ))
                    continue
                # linhas que não combinam com nada são ignoradas
                # (normalmente continuações de títulos quebrados — ajustaremos
                # numa revisão posterior ao comparar contagem com 1029)

    # Sanity check
    ids = [a.id for a in apostilas]
    expected = list(range(1, 1030))
    missing = [i for i in expected if i not in ids]
    duplicates = [i for i in ids if ids.count(i) > 1]

    data = {
        "versao_mapa": "EBE-PLAN-APO (edição 2026)",
        "total_esperado": 1029,
        "total_extraido": len(apostilas),
        "faltantes": missing,
        "duplicados": sorted(set(duplicates)),
        "niveis": _agrupar_por_nivel(apostilas),
        "apostilas": [asdict(a) for a in sorted(apostilas, key=lambda x: x.id)],
    }
    return data


def _agrupar_por_nivel(apostilas: list[Apostila]) -> list[dict]:
    niveis: dict[int, dict] = {}
    for a in apostilas:
        n = niveis.setdefault(a.nivel_id, {"id": a.nivel_id, "nome": a.nivel,
                                           "institutos": {}})
        inst = n["institutos"].setdefault(a.instituto_id,
                                          {"id": a.instituto_id,
                                           "nome": a.instituto,
                                           "escolas": {}})
        esc = inst["escolas"].setdefault(a.escola,
                                         {"nome": a.escola,
                                          "cursos": {}})
        cur = esc["cursos"].setdefault(a.curso_id,
                                       {"id": a.curso_id,
                                        "nome": a.curso,
                                        "carga_horaria": a.carga_horaria,
                                        "modulos": {}})
        mod = cur["modulos"].setdefault(a.modulo_id,
                                        {"id": a.modulo_id,
                                         "nome": a.modulo,
                                         "apostilas": []})
        mod["apostilas"].append({"id": a.id, "numero": a.numero, "titulo": a.titulo})

    out = []
    for nid in sorted(niveis):
        n = niveis[nid]
        n["institutos"] = [
            {**inst, "id": iid,
             "escolas": [
                {**esc, "nome": enome,
                 "cursos": [
                    {**cur, "id": cid,
                     "modulos": [
                        {**mod, "id": mid} for mid, mod in sorted(cur["modulos"].items())
                     ]} for cid, cur in esc["cursos"].items()
                 ]} for enome, esc in inst["escolas"].items()
             ]} for iid, inst in n["institutos"].items()
        ]
        out.append(n)
    return out


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = parse()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Total extraído: {data['total_extraido']} / esperado 1029")
    print(f"Faltantes ({len(data['faltantes'])}): {data['faltantes'][:20]}...")
    print(f"Duplicados: {data['duplicados']}")
    print(f"Gravado em: {OUT}")


if __name__ == "__main__":
    main()
