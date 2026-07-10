"""Escola Bíblica Epignósis — Pacote do sistema de geração de materiais."""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ebe")
except PackageNotFoundError:
    __version__ = "0.1.0"
