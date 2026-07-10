"""Exceções customizadas do projeto EBE."""


class EBEError(Exception):
    """Exceção base do projeto."""

    pass


class ConfigError(EBEError):
    """Erro de configuração."""

    pass


class CurriculumError(EBEError):
    """Erro no processamento do currículo."""

    pass


class DocumentError(EBEError):
    """Erro na geração de documento."""

    pass


class OriginalityError(EBEError):
    """Erro na verificação de originalidade."""

    pass


class GeminiError(EBEError):
    """Erro na comunicação com API Gemini."""

    pass


class RateLimitError(EBEError):
    """Limite de taxa excedido."""

    pass
