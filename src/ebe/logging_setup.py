"""Configuração centralizada de logging do sistema."""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path

# Expressão para detectar chaves Google AI (começam normalmente por AIza… seguido de ~35 chars)
_RE_KEY = re.compile(r"AIza[0-9A-Za-z\-_]{20,}")
_RE_GENERIC_TOKEN = re.compile(r"\b[A-Za-z0-9_\-]{30,}\b")


class _RedactFilter(logging.Filter):
    """Filtro que remove qualquer chave/token antes de escrever nos logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            if isinstance(record.msg, str):
                record.msg = _redact(record.msg)
            if record.args:
                if isinstance(record.args, dict):
                    record.args = {k: _redact(str(v)) for k, v in record.args.items()}
                elif isinstance(record.args, tuple):
                    record.args = tuple(_redact(str(a)) for a in record.args)
        except Exception:
            # Nunca deixar uma falha de redacção derrubar a execução
            pass
        return True


def _redact(text: str) -> str:
    text = _RE_KEY.sub("[REDACTED_API_KEY]", text)
    # Não aplicar o genérico — pode capturar texto longo comum (como markdown).
    return text


def setup_logging(log_dir: str | os.PathLike = "state/logs",
                  level: int = logging.INFO) -> tuple[logging.Logger, Path]:
    """Configura logging para consola e ficheiro de execução.

    Retorna (logger, caminho_do_ficheiro_de_log).
    """
    log_dir_p = Path(log_dir)
    log_dir_p.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    log_file = log_dir_p / f"run-{ts}.log"

    logger = logging.getLogger("ebe")
    logger.setLevel(level)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    fh.addFilter(_RedactFilter())
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.addFilter(_RedactFilter())
    logger.addHandler(ch)

    logger.propagate = False
    logger.info("Logging inicializado em %s", log_file)
    return logger, log_file
