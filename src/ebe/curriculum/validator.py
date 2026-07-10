"""Valida integridade do curriculum.json (1.029 IDs, sem lacunas, sem duplicados)."""
from __future__ import annotations

from ..exceptions import CurriculumValidationError


def validate(data: dict, expected_total: int = 1029) -> list[str]:
    """Valida o curriculum carregado. Devolve lista de erros (vazia se tudo ok)."""
    erros: list[str] = []
    apos = data.get("apostilas")
    if not isinstance(apos, list):
        erros.append("chave 'apostilas' em falta ou não é lista")
        return erros

    if len(apos) != expected_total:
        erros.append(f"total de apostilas = {len(apos)} (esperado {expected_total})")

    ids = [a.get("id") for a in apos if isinstance(a, dict)]
    expected = set(range(1, expected_total + 1))
    got = set(ids)
    missing = expected - got
    if missing:
        amostra = sorted(missing)[:10]
        erros.append(f"IDs em falta ({len(missing)}): {amostra}{'...' if len(missing) > 10 else ''}")
    extra = got - expected
    if extra:
        erros.append(f"IDs fora do intervalo: {sorted(extra)[:10]}")

    # Verifica duplicados
    from collections import Counter
    dup = [i for i, c in Counter(ids).items() if c > 1]
    if dup:
        erros.append(f"IDs duplicados: {sorted(dup)}")

    # Campos obrigatórios por apostila
    obrig = ["id", "numero", "titulo", "modulo", "curso", "escola", "instituto", "nivel"]
    for a in apos:
        if not isinstance(a, dict):
            continue
        for k in obrig:
            if k not in a or not a[k]:
                erros.append(f"apostila id={a.get('id')} sem campo '{k}'")
                break

    return erros


def validate_or_raise(data: dict, expected_total: int = 1029) -> None:
    erros = validate(data, expected_total=expected_total)
    if erros:
        raise CurriculumValidationError("Curriculum inválido:\n  - " + "\n  - ".join(erros))
