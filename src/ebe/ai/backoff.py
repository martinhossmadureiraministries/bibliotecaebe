"""Política de retry com exponential backoff + jitter."""
from __future__ import annotations

import logging
import random
import time
from typing import Callable, TypeVar

from tenacity import (
    RetryError, Retrying, retry_if_exception_type, stop_after_attempt,
    wait_exponential_jitter,
)

from . import gemini_client as gc

log = logging.getLogger("ebe.backoff")

T = TypeVar("T")


def is_retryable(exc: Exception) -> bool:
    from ..exceptions import QuotaExceededError, AIError
    # 429 (quota) e erros 5xx/de rede são retentáveis
    if isinstance(exc, (QuotaExceededError,)):
        return True
    if isinstance(exc, gc.GeminiRateLimitError):
        return True
    if isinstance(exc, gc.GeminiTransientError):
        return True
    if isinstance(exc, gc.GeminiServerError):
        return True
    return False


def with_backoff(fn: Callable[[], T], max_attempts: int = 5,
                 initial: float = 2.0, maximum: float = 90.0) -> T:
    """Executa fn com retry exponencial. Propaga a excepção após esgotar tentativas."""
    retryer = Retrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential_jitter(initial=initial, max=maximum, jitter=(0.5, 2.0)),
        retry=retry_if_exception_type()(lambda e: is_retryable(e)),
        before_sleep=lambda s: log.warning(
            "Tentativa %s falhou: %s. A aguardar %.1fs…",
            s.attempt_number,
            type(s.outcome.exception()).__name__ if s.outcome and s.outcome.exception() else "?",
            s.next_action.sleep if s.next_action else 0,
        ),
        reraise=True,
    )
    try:
        return retryer(fn)
    except RetryError as e:
        raise e.last_attempt.exception()  # type: ignore[misc]
