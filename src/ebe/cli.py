"""Interface CLI para EBE — Sistema de Geração de Apostilas."""

import click
from pathlib import Path
import sys

from . import __version__
from .config import ensure_dirs, PROJECT_ROOT, GEMINI_API_KEY
from .logging_config import setup_logging

logger = setup_logging(__name__)


@click.group()
@click.version_option(version=__version__)
def cli():
    """Sistema de Geração de Apostilas da Escola Bíblica Epignósis."""
    ensure_dirs()


@cli.command()
def info():
    """Mostra informações do projeto."""
    click.echo(f"\n📚 Escola Bíblica Epignósis — Geração de Apostilas")
    click.echo(f"   Versão: {__version__}")
    click.echo(f"   Raiz: {PROJECT_ROOT}")
    click.echo(f"   Status API Gemini: {'✅ Configurada' if GEMINI_API_KEY else '⚠️  Não configurada'}")
    click.echo()


@cli.command()
def init():
    """Inicializa o repositório (cria diretórios, valida configuração)."""
    click.echo("\n🔧 Inicializando EBE...")
    try:
        ensure_dirs()
        click.echo("✅ Diretórios criados.")

        if not GEMINI_API_KEY:
            click.secho(
                "⚠️  GEMINI_API_KEY não está configurada.\n"
                "   Consulte docs/GEMINI_SETUP.md para instruções.",
                fg="yellow",
            )
        else:
            click.secho("✅ GEMINI_API_KEY detectada.", fg="green")

        click.echo("\n✨ Inicialização concluída!\n")
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--count",
    default=1,
    help="Número de apostilas a gerar.",
    type=int,
)
def generate(count: int):
    """Gera apostilas (requer GEMINI_API_KEY)."""
    click.echo(f"\n🚀 Gerando {count} apostila(s)...")
    click.echo("   (Funcionalidade em desenvolvimento para M2)")
    click.echo()


if __name__ == "__main__":
    cli()
