"""CLI principal do sistema EBE (python -m ebe <comando>)."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from . import __version__
from .config import load_config


@click.group()
@click.version_option(__version__, prog_name="ebe")
def cli() -> None:
    """Sistema de geração de apostilas e materiais da Escola Bíblica Epignósis."""


@cli.command("status")
def cmd_status() -> None:
    """Mostra o estado actual do projecto (para ser lido no telemóvel)."""
    cfg = load_config()
    click.echo(f"EBE v{__version__}")
    click.echo(f"Mapa activo: {cfg.curriculum.active_map}")
    # Resumo do curriculum
    import json
    curr = cfg.repo_path(cfg.caminhos.curriculum_ativo)
    if curr.exists():
        data = json.loads(curr.read_text(encoding="utf-8"))
        click.echo(f"Total de apostilas no mapa: {data.get('total_extraido')}")
    else:
        click.echo("(curriculum.json não encontrado)")
    # Registro
    reg = cfg.repo_path(cfg.caminhos.registry)
    if reg.exists():
        n = sum(1 for _ in reg.open(encoding="utf-8"))
        click.echo(f"Apostilas registadas: {n}")
    else:
        click.echo("Apostilas registadas: 0")


@cli.command("next")
def cmd_next() -> None:
    """Mostra a próxima apostila pendente (sem gerar)."""
    from .curriculum.repository import CurriculumRepository
    from .registry.manager import RegistryManager
    cfg = load_config()
    curr = CurriculumRepository(cfg)
    reg = RegistryManager(cfg)
    pend = curr.next_pending(reg.done_ids(), n=1)
    if not pend:
        click.echo("Nenhuma apostila pendente. Mapa concluído!")
        return
    a = pend[0]
    click.echo(f"Próxima apostila:  #{a.numero} — {a.titulo}")
    click.echo(f"  Nível {a.nivel_id} · Instituto {a.instituto_id}")
    click.echo(f"  Escola: {a.escola}")
    click.echo(f"  Curso:  {a.curso}")
    click.echo(f"  Módulo: {a.modulo}")


@cli.command("diag")
def cmd_diag() -> None:
    """Autodiagnóstico rápido."""
    from .core.autodiagnostico import run_diag
    cfg = load_config()
    report = run_diag(cfg)
    for k, v in report.items():
        click.echo(f"  [{ 'OK' if v else '!!' }] {k}")


@cli.command("generate")
@click.option("--id", "ids", multiple=True, type=int, help="ID(s) específico(s) a gerar.")
@click.option("--count", default=1, type=int, help="Número de apostilas a gerar (default 1).")
@click.option("--dry-run", is_flag=True, help="Apenas mostra o que faria, sem chamar a IA.")
@click.option("--simulate-ai", is_flag=True, help="Usa IA simulada (para testar sem chave).")
def cmd_generate(ids, count, dry_run, simulate_ai) -> None:
    """Gera apostila(s) pendentes."""
    from .core.pipeline import run_pipeline
    cfg = load_config()
    run_pipeline(cfg,
                 especificos=list(ids) if ids else None,
                 count=count,
                 dry_run=dry_run,
                 simulate_ai=simulate_ai)


if __name__ == "__main__":
    cli()
