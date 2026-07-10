"""Token bucket rate limiter para respeitar TPM/RPM/RPD da API Gemini."""
from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass


@dataclass
class RateLimiterConfig:
    rpm: int = 5           # requests per minute
    tpm: int = 500_000     # tokens per minute
    rpd: int = 1_000       # requests per day


class RateLimiter:
    """Limita chamadas por minuto/dia e tokens por minuto."""

    def __init__(self, cfg: RateLimiterConfig | None = None):
        self.cfg = cfg or RateLimiterConfig()
        self._req_minute: deque[float] = deque()
        self._req_day: deque[float] = deque()
        self._tokens_minute: deque[tuple[float, int]] = deque()
        self._lock = threading.Lock()

    def _prune(self) -> None:
        now = time.time()
        while self._req_minute and now - self._req_minute[0] > 60:
            self._req_minute.popleft()
        while self._req_day and now - self._req_day[0] > 86400:
            self._req_day.popleft()
        while self._tokens_minute and now - self._tokens_minute[0][0] > 60:
            self._tokens_minute.popleft()

    def _wait_needed(self, tokens_estimate: int) -> float:
        self._prune()
        wait = 0.0
        if len(self._req_minute) >= self.cfg.rpm:
            wait = max(wait, 60 - (time.time() - self._req_minute[0]))
        if len(self._req_day) >= self.cfg.rpd:
            wait = max(wait, 86400 - (time.time() - self._req_day[0]))
        tokens_sum = sum(t for _, t in self._tokens_minute)
        if tokens_sum + tokens_estimate > self.cfg.tpm and self._tokens_minute:
            wait = max(wait, 60 - (time.time() - self._tokens_minute[0][0]))
        return wait

    def acquire(self, tokens_estimate: int = 5000, max_wait: float = 600) -> None:
        """Bloqueia até que seja permitido fazer o pedido."""
        start = time.time()
        while True:
            with self._lock:
                w = self._wait_needed(tokens_estimate)
                if w <= 0:
                    now = time.time()
                    self._req_minute.append(now)
                    self._req_day.append(now)
                    self._tokens_minute.append((now, tokens_estimate))
                    return
            if time.time() - start > max_wait:
                raise RuntimeError("RateLimiter: tempo de espera excedido")
            time.sleep(min(w, 5))

    def record_tokens(self, actual_tokens: int) -> None:
        """Ajusta contagem de tokens com o valor real devolvido pela API."""
        with self._lock:
            if self._tokens_minute:
                t_old, est = self._tokens_minute[-1]
                self._tokens_minute[-1] = (t_old, actual_tokens)

    @property
    def stats(self) -> dict:
        with self._lock:
            self._prune()
            return {
                "requests_last_minute": len(self._req_minute),
                "requests_last_day": len(self._req_day),
                "tokens_last_minute": sum(t for _, t in self._tokens_minute),
                "rpm_limit": self.cfg.rpm,
                "tpm_limit": self.cfg.tpm,
                "rpd_limit": self.cfg.rpd,
            }
