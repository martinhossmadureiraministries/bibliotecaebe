"""Configuração de logging estruturado."""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """Formata logs como JSON estruturado."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    structured: bool = False,
) -> logging.Logger:
    """Configura logger com handlers console e ficheiro.

    Args:
        name: Nome do logger (tipicamente __name__)
        level: Nível mínimo (INFO, DEBUG, etc.)
        log_file: Caminho opcional para ficheiro de log
        structured: Se True, usa formatação JSON

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Handler console
    ch = logging.StreamHandler()
    ch.setLevel(level)
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Handler ficheiro (opcional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
