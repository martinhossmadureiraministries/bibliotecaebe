"""Gestão de templates de prompt (Jinja2)."""
from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

PROMPTS_DIR = Path(__file__).parent


def get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(PROMPTS_DIR)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(name: str, **ctx) -> str:
    env = get_env()
    tpl = env.get_template(name)
    return tpl.render(**ctx)
