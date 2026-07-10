"""Exceções tipadas do sistema."""
from __future__ import annotations


class EBEError(Exception):
    """Classe base para todas as excepções do sistema."""


# ------ Curriculum ------
class CurriculumError(EBEError):
    """Erros relacionados ao mapa curricular."""


class CurriculumValidationError(CurriculumError):
    """Mapa inválido (ex: IDs em falta, duplicados, hierarquia inconsistente)."""


# ------ AI / Gemini ------
class AIError(EBEError):
    """Erros na geração de conteúdo via IA."""


class QuotaExceededError(AIError):
    """Quota diária / por minuto esgotada — retomável após espera."""


class InvalidResponseError(AIError):
    """Resposta da IA não corresponde ao formato esperado."""


class OriginalityError(AIError):
    """Similaridade acima do limiar após todas as tentativas."""


# ------ DOCX ------
class DocxBuildError(EBEError):
    """Erros na montagem do DOCX."""


class PageCountError(DocxBuildError):
    """Documento fora de 15–20 páginas após as tentativas de ajuste."""


# ------ Registry / Estado ------
class RegistryError(EBEError):
    """Erros no registo de apostilas."""


class StateCorruptionError(EBEError):
    """Ficheiro de estado ilegível / corrompido."""


# ------ Configuração ------
class ConfigError(EBEError):
    """Configuração inválida ou em falta."""
