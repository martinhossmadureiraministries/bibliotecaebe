"""Geração automática do PROJECT_STATE.md (painel de progresso)."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ..config import Config, REPO_ROOT

MARK_BEGIN = "<!-- AUTO:STATE:BEGIN -->"
MARK_END = "<!-- AUTO:STATE:END -->"


def _git_head() -> str:
    try:
        r = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return "?"


def _git_branch() -> str:
    try:
        r = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return "?"


def _load_registry(cfg: Config) -> list[dict]:
    p = cfg.repo_path(cfg.caminhos.registry)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _load_last_error(cfg: Config) -> str:
    p = cfg.repo_path("state/last_error.json")
    if not p.exists():
        return "—"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return f"{d.get('when', '')} · {d.get('apostila', '')} · {d.get('error', '')}"
    except Exception:
        return "—"


def _progress_bar(done: int, total: int, size: int = 40) -> str:
    f = done / total if total else 0
    n = int(f * size)
    bar = "█" * n + "░" * (size - n)
    return f"[{bar}] {done}/{total}  ({f*100:.1f}%)"


def build_state(cfg: Config) -> str:
    import os
    curr_path = cfg.repo_path(cfg.caminhos.curriculum_ativo)
    curr = json.loads(curr_path.read_text(encoding="utf-8"))
    total = curr.get("total_extraido", 1029)
    reg = _load_registry(cfg)
    done_entries = [r for r in reg if r.get("status") in {"generated", "validated"}]
    done = len(done_entries)
    last = done_entries[-1] if done_entries else None
    # Próxima
    done_ids = {r["id"] for r in done_entries}
    next_ap = None
    for a in curr.get("apostilas", []):
        if a["id"] not in done_ids:
            next_ap = a
            break

    has_key = bool(os.environ.get("GEMINI_API_KEY") or cfg.gemini.api_key)
    api_status = "OK (chave detectada)" if has_key else "**não configurada**"

    lines = []
    lines.append("")
    lines.append(f"**Última actualização:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Versão do sistema:** {cfg.geral.sistema_versao}")
    lines.append(f"**Mapa activo:** `{cfg.curriculum.active_map}` (total {total} apostilas)")
    lines.append(f"**Ramo de trabalho:** `{_git_branch()}` (commit `{_git_head()}`)")
    lines.append("")
    lines.append("## Progresso geral")
    lines.append("")
    lines.append("| Indicador | Valor |")
    lines.append("|-----------|-------|")
    lines.append(f"| Apostilas criadas (finalizadas) | **{done} / {total}** |")
    lines.append(f"| Apostilas restantes | **{total - done}** |")
    if last:
        lines.append(f"| Última apostila gerada | **#{last['numero']} — {last['titulo']}** ({last.get('data_geracao','')[:10]}) |")
    else:
        lines.append(f"| Última apostila gerada | — (nenhuma) |")
    if next_ap:
        lines.append(f"| Próxima apostila | **#{next_ap['numero']} — {next_ap['titulo']}** (N{next_ap['nivel_id']} · I{next_ap['instituto_id']} · {next_ap['escola']} · {next_ap['curso']}) |")
    else:
        lines.append(f"| Próxima apostila | — mapa concluído! |")
    logs_dir = cfg.repo_path(cfg.caminhos.logs_dir)
    ultimo_log = "—"
    if logs_dir.exists():
        lfs = sorted([p.name for p in logs_dir.glob("*.log")])
        if lfs:
            ultimo_log = lfs[-1]
    lines.append(f"| Último log | `{ultimo_log}` |")
    lines.append(f"| Último erro | {_load_last_error(cfg)} |")
    lines.append(f"| Estado da API Gemini | {api_status} |")
    lines.append(f"| Saldo diário (meta: {cfg.geral.apostilas_por_dia}/dia) | em actualização contínua |")
    lines.append("")
    lines.append(f"```")
    lines.append(_progress_bar(done, total))
    lines.append(f"```")
    lines.append("")
    return "\n".join(lines)


def write_state(cfg: Config, path: Path | None = None) -> Path:
    out = path or (REPO_ROOT / "PROJECT_STATE.md")
    original = out.read_text(encoding="utf-8") if out.exists() else ""
    if MARK_BEGIN not in original or MARK_END not in original:
        # Se o ficheiro não existe com as marcas, criamos um template mínimo.
        original = (
            "# PROJECT STATE · Sistema de Geração de Apostilas EBE\n"
            "> Actualizado automaticamente. **Não editar** entre as marcas `<!-- AUTO:STATE:BEGIN/END -->`.\n\n"
            f"{MARK_BEGIN}\n{MARK_END}\n"
        )
    novo = build_state(cfg)
    before, _, after = original.partition(MARK_BEGIN)
    _, _, after = after.partition(MARK_END)
    final = f"{before}{MARK_BEGIN}{novo}\n{MARK_END}{after}"
    out.write_text(final, encoding="utf-8")
    return out
