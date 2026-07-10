"""Wrapper seguro do cliente Google Gemini com rate limiting, retry e cache de contexto.

Inclui modo `simulate` que devolve respostas sintéticas (para testar o pipeline
sem precisar de chave API).
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

from ..config import Config
from ..exceptions import AIError, ConfigError, InvalidResponseError, QuotaExceededError
from .rate_limiter import RateLimiter, RateLimiterConfig

log = logging.getLogger("ebe.gemini")


class GeminiError(AIError):
    pass


class GeminiAuthError(GeminiError):
    pass


class GeminiRateLimitError(GeminiError):
    pass


class GeminiServerError(GeminiError):
    pass


class GeminiTransientError(GeminiError):
    pass


@dataclass
class GeminiResponse:
    text: str
    tokens_in: int = 0
    tokens_out: int = 0
    model: str = ""
    cached: bool = False


class GeminiClient:
    """Cliente Gemini com rate-limiter e modo simulação."""

    def __init__(self, cfg: Config, simulate: bool = False):
        self.cfg = cfg
        self.simulate = simulate
        g = cfg.gemini
        self.api_key = g.api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model_name = g.modelo_geracao
        self.embedding_model = g.modelo_embeddings
        self.timeout = g.timeout_segundos
        # No modo simulação, usamos limites altos para não travar testes.
        if simulate:
            self.rate_limiter = RateLimiter(RateLimiterConfig(rpm=1000, tpm=10_000_000, rpd=100_000))
        else:
            self.rate_limiter = RateLimiter(RateLimiterConfig(rpm=g.rpm, tpm=g.tpm, rpd=g.rpd))
        self._model = None
        self._emb_client = None
        self._cache_name: Optional[str] = None

        if not simulate:
            if not self.api_key:
                raise ConfigError("GEMINI_API_KEY não configurada (secrets/env).")
            try:
                import google.generativeai as genai  # type: ignore
            except ImportError:
                raise ConfigError("Pacote 'google-generativeai' não instalado. pip install -r requirements.txt")
            genai.configure(api_key=self.api_key)
            self._genai = genai
            self._model = genai.GenerativeModel(self.model_name)
        else:
            log.warning("GeminiClient em modo SIMULATE — respostas serão sintéticas.")

    # ------------------------------------------------------------------
    def generate(self, prompt: str, system_instruction: Optional[str] = None,
                 max_tokens: int = 8192, temperature: float = 0.7) -> GeminiResponse:
        """Gera texto. Respeita rate limit e aplica retry no caller (via backoff.py)."""
        self.rate_limiter.acquire(tokens_estimate=min(max_tokens, 4096))
        if self.simulate:
            return self._simulated_response(prompt)
        try:
            from google.api_core import exceptions as gexc  # type: ignore
            kwargs: dict[str, Any] = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if system_instruction:
                # Se temos cached content, usámo-lo; senão enviamos system_instruction normal.
                if self._cache_name:
                    kwargs["cached_content"] = self._cache_name
                else:
                    m = self._genai.GenerativeModel(
                        self.model_name,
                        system_instruction=system_instruction,
                    )
                    resp = m.generate_content(prompt, generation_config=kwargs)
                    return self._to_response(resp, model=self.model_name)
            resp = self._model.generate_content(prompt, generation_config=kwargs)
            return self._to_response(resp, model=self.model_name)
        except Exception as e:  # pragma: no cover
            self._translate_exception(e)

    def embed(self, text: str) -> list[float]:
        """Devolve embedding vectorial para controlo de similaridade."""
        self.rate_limiter.acquire(tokens_estimate=1024)
        if self.simulate:
            # Embedding pseudo-aleatório e determinístico baseado em hash, mas
            # com projecção ruidosa para que textos diferentes sejam distintos
            # mas estáveis. Usamos um "random" com seed baseado no hash.
            import hashlib
            import random as _r
            seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % (2**32)
            rng = _r.Random(seed)
            vec = [rng.gauss(0, 1) for _ in range(768)]
            norm = sum(v*v for v in vec) ** 0.5
            return [v/norm for v in vec]
        try:
            resp = self._genai.embed_content(
                model=f"models/{self.embedding_model}",
                content=text,
                task_type="SEMANTIC_SIMILARITY",
            )
            vals = resp.get("embedding", {}).get("values", []) if isinstance(resp, dict) else resp.embedding
            return list(vals)
        except Exception as e:  # pragma: no cover
            self._translate_exception(e)

    def cache_system(self, system_instruction: str, ttl_seconds: int = 3600) -> Optional[str]:
        """Cria um CachedContent para o system_instruction (reduz tokens).
        Devolve o nome do cache ou None em modo simulação / sem suporte."""
        if self.simulate:
            self._cache_name = "simulated-cache"
            return self._cache_name
        try:
            from google.ai import generativelanguage as glm  # type: ignore
            from datetime import timedelta
            client = glm.CacheServiceClient()
            from google.protobuf import duration_pb2
            c = client.create_cached_content(
                cached_content=glm.CachedContent(
                    model=f"models/{self.model_name}",
                    system_instruction=glm.Content(parts=[glm.Part(text=system_instruction)]),
                    ttl=duration_pb2.Duration(seconds=ttl_seconds),
                    display_name="ebe-system",
                )
            )
            self._cache_name = c.name
            log.info("Cached content criado: %s", c.name)
            return c.name
        except Exception as e:
            log.warning("Context caching indisponível ou falhou: %s", e)
            self._cache_name = None
            return None

    # ------------------------------------------------------------------
    def _to_response(self, resp, model: str) -> GeminiResponse:
        try:
            text = resp.text
        except Exception:
            # Quando há bloqueios de segurança, resp.text pode levantar
            raise InvalidResponseError(f"Resposta vazia/bloqueada: {getattr(resp, 'prompt_feedback', resp)}")
        tokens_in = 0
        tokens_out = 0
        try:
            usage = resp.usage_metadata
            tokens_in = usage.prompt_token_count
            tokens_out = usage.candidates_token_count
        except Exception:
            pass
        self.rate_limiter.record_tokens(tokens_in + tokens_out)
        return GeminiResponse(text=text, tokens_in=tokens_in, tokens_out=tokens_out,
                              model=model, cached=bool(self._cache_name))

    def _simulated_response(self, prompt: str) -> GeminiResponse:
        """Resposta sintética rica, suficiente para exercitar o pipeline completo.
        Extrai o número e título da apostila a partir do prompt quando possível."""
        import re
        titulo = "o tema"
        m = re.search(r'Apostila N\.\º\s*(\d+)\s+[—-]\s+"([^"]+)"', prompt)
        if m:
            titulo = m.group(2)
        lowered = prompt.lower()
        if "outline" in lowered or "json com a estrutura" in lowered or "dev" in lowered:
            payload = self._simulated_outline(titulo)
        elif "conteudo textual de uma sec" in lowered or "secção" in lowered or "secao" in lowered:
            payload = self._simulated_section(titulo)
        else:
            payload = {"ok": True, "placeholder": True}
        return GeminiResponse(text=json.dumps(payload, ensure_ascii=False),
                              tokens_in=100, tokens_out=800, model="simulate", cached=False)

    def _simulated_outline(self, titulo: str) -> dict:
        lorem = (
            f"Esta secção introduz o tema de {titulo}, mostrando a sua relevância "
            f"para a vida cristã e para o ministério da Palavra. A partir das Escrituras, "
            f"procuramos fundamentar a doutrina com clareza e aplicá-la com pastoralidade."
        )
        return {
            "versiculo_chave": {"texto": "Procura apresentar-te a Deus aprovado, como obreiro que não tem de que se envergonhar, que maneja bem a palavra da verdade.",
                                "referencia": "2 Timóteo 2.15"},
            "texto_base": "Romanos 1.16-17; 2 Timóteo 2.15",
            "subtitulo": f"Uma introdução a {titulo}",
            "apresentacao": [
                f"Esta apostila inaugura o estudo de {titulo}, oferecendo os fundamentos bíblicos necessários para uma compreensão sólida e aplicada.",
                "Ao longo das próximas páginas, o(a) aluno(a) será conduzido(a) a examinar as Escrituras com atenção, relacionando o tema com a vida e o ministério.",
                "Nosso objectivo é glorificar a Deus por meio de um ensino fiel, claro e edificante."
            ],
            "objectivos": [
                f"CONHECER — identificar os principais textos bíblicos e doutrinas relacionados a {titulo}.",
                f"CRER — interiorizar a verdade de {titulo} como fundamento da fé cristã.",
                f"VIVER — aplicar {titulo} na vida devocional, familiar e comunitária.",
                f"SERVIR — comunicar e ensinar {titulo} com fidelidade no contexto da igreja local.",
            ],
            "introducao": [
                "Desde os primeiros capítulos das Escrituras, Deus revela-se de forma progressiva, convidando o seu povo a conhecê-Lo em verdade.",
                f"Compreender {titulo} não é um exercício meramente intelectual; é uma resposta de obediência e adoração diante da Palavra.",
                "Nas secções que se seguem, examinaremos o tema a partir de suas bases bíblicas, das suas implicações práticas e dos equívocos a evitar."
            ],
            "secoes": [
                {"titulo": "Fundamentos bíblicos do tema",
                 "paragrafos_count": 4,
                 "citacoes": [{"texto": "Toda a Escritura é divinamente inspirada e proveitosa para ensinar, para redarguir, para corrigir, para instruir em justiça.", "referencia": "2 Timóteo 3.16"}],
                 "lista_ordenada_count": 0,
                 "lista_marcada_count": 3,
                 "caixas": [{"titulo": "Para reter", "texto": "A autoridade da Escritura é o fundamento de todo o ensino fiel."}],
                 "tabelas": [],
                 "subsecoes": []},
                {"titulo": "Clarificação conceitual",
                 "paragrafos_count": 4,
                 "citacoes": [],
                 "lista_ordenada_count": 3,
                 "lista_marcada_count": 0,
                 "caixas": [],
                 "tabelas": [{"cabecalho": ["Conceito", "Definição"], "linhas": [[titulo, f"Definição bíblica de {titulo}"]]}],
                 "subsecoes": []},
                {"titulo": "Implicações práticas para a vida cristã",
                 "paragrafos_count": 4,
                 "citacoes": [{"texto": "Sede, pois, praticantes da palavra e não somente ouvidores, enganando-vos a vós mesmos.", "referencia": "Tiago 1.22"}],
                 "lista_ordenada_count": 0,
                 "lista_marcada_count": 3,
                 "caixas": [],
                 "tabelas": [],
                 "subsecoes": []},
                {"titulo": "Equívocos e dúvidas comuns",
                 "paragrafos_count": 2,
                 "citacoes": [],
                 "lista_ordenada_count": 0,
                 "lista_marcada_count": 0,
                 "caixas": [],
                 "tabelas": [],
                 "subsecoes": [
                    {"titulo": "Equívoco 1 — Reduzir o tema a mero conhecimento intelectual", "paragrafos_count": 2},
                    {"titulo": "Equívoco 2 — Separar a doutrina da vida", "paragrafos_count": 2},
                 ]},
                {"titulo": "Quadro de destaque — para reter",
                 "paragrafos_count": 1,
                 "citacoes": [],
                 "lista_ordenada_count": 0,
                 "lista_marcada_count": 0,
                 "caixas": [{"titulo": "✦ Para reter", "texto": f"{titulo} deve ser compreendido à luz da totalidade das Escrituras, aplicado pelo Espírito Santo e vivido na comunidade da fé."}],
                 "tabelas": [],
                 "subsecoes": []},
            ],
            "aplicacao_pratica": [
                "A doutrina bíblica não se encerra em si mesma; ela deve transformar a vida do(a) discípulo(a) em todas as áreas da sua existência."
            ],
            "aplicacao_itens": [
                f"Na vida devocional — reserve um tempo diário de oração e meditação em passagens relativas a {titulo}.",
                f"Na família — partilhe com o cônjuge e os filhos o que tem aprendido sobre {titulo}.",
                f"Na igreja local — procure ensinar e discutir {titulo} com os irmãos, em espírito de mansidão.",
                "Na sociedade — viva de forma coerente com o que crê, testemunhando com palavras e obras.",
                f"No ministério — ao ensinar {titulo}, fundamente-se sempre na Palavra e no exemplo de Cristo.",
            ],
            "sintese": [
                f"Ao longo desta apostila, vimos que {titulo} está firmemente fundamentado nas Escrituras e tem implicações directas para a vida cristã.",
                "Que o Espírito Santo nos conceda graça para viver o que temos aprendido, para glória de Deus e edificação do corpo de Cristo.",
                "Soli Deo Gloria."
            ],
            "exercicios": [
                {"titulo": "I — Verifique a sua compreensão",
                 "itens": [f"Defina {titulo} com suas próprias palavras.", "Quais são os principais textos bíblicos que sustentam o tema?", "Explique a relação entre doutrina e vida cristã.", "Cite um equívoco comum sobre o tema e explique por que é inadequado."]},
                {"titulo": "II — Reflexão pessoal",
                 "itens": [f"De que forma {titulo} desafia o seu modo de viver actual?", "Que atitude concreta adoptará nesta semana em resposta ao estudo?", "Escreva uma oração de resposta ao Senhor."]},
                {"titulo": "III — Ministério e serviço",
                 "itens": [f"Como explicaria {titulo} a um novo convertido em 3 minutos?", "Que oportunidade concreta tem de ensinar ou partilhar este tema na sua igreja?"]},
            ],
            "estudo_complementar": {
                "titulo": "2 Timóteo 2.14-26 — O obreiro aprovado",
                "texto": f"Leia 2 Timóteo 2.14-26 e observe como Paulo exorta Timóteo a manejar bem a palavra da verdade, em conexão com o tema {titulo}.",
                "perguntas": ["Quais são as características do obreiro aprovado?", "Como evitar contendas inúteis?", "De que forma a paciência se relaciona com o ensino fiel?", "Qual o resultado do ensino fiel?"]
            },
            "proxima_apostila": {
                "titulo": "A próxima secção do curso",
                "descricao": "Na próxima apostila continuaremos o estudo, aprofundando os elementos práticos que decorrem desta base doutrinária.",
                "preparar": ["Leia a passagem bíblica indicada para a próxima apostila.", "Reflicta sobre as aplicações práticas do tema.", "Anote as dúvidas que surgiram no estudo pessoal."]
            },
            "glossario": [
                {"termo": "Escritura", "definicao": "Conjunto dos livros bíblicos do Antigo e Novo Testamento, reconhecidos como Palavra de Deus inspirada."},
                {"termo": "Doutrina", "definicao": "Ensino bíblico estruturado e fiel, destinado à edificação da Igreja."},
                {"termo": "Fé", "definicao": "Confiança em Deus e na sua Palavra, que inclui conhecimento, assentimento e entrega pessoal."},
                {"termo": "Graça", "definicao": "Favor imerecido de Deus em Cristo para salvação e vida cristã."},
                {"termo": "Obediência", "definicao": "Resposta fiel à Palavra de Deus, motivada pelo amor e pela graça recebida."},
                {"termo": "Ministério", "definicao": "Serviço cristão em favor da Igreja e do mundo, no poder do Espírito Santo."},
            ],
            "bibliografia": [
                "Bíblia Sagrada. Tradução de João Ferreira de Almeida, Revista e Corrigida.",
                "CALVINO, João. Institutas da Religião Cristã. São Paulo: Cultura Cristã.",
                "BERKHOF, Louis. Teologia Sistemática. São Paulo: Cultura Cristã.",
                "PACKER, J. I. Conhecendo a Deus. São Paulo: Cultura Cristã.",
                "STOTT, John R. W. O povo de Deus. São Paulo: ABU.",
            ]
        }

    def _simulated_section(self, titulo: str) -> dict:
        return {
            "paragrafos": [
                f"Ao abordar o tema de {titulo}, é necessário começar por reconhecer que as Escrituras falam com clareza e autoridade, chamando o(a) crente a uma compreensão fiel e reverente.",
                "Diversas passagens convergem para o mesmo ensino, demonstrando a coesão da revelação bíblica e a necessidade de interpretar texto com texto, à luz da totalidade do conselho de Deus.",
                "Uma compreensão adequada deste ponto produz impacto directo na vida diária, pois muda a forma como oramos, adoramos, nos relacionamos e servimos no corpo de Cristo.",
                "Por isso, não basta conhecer doutrinas abstractas: o Espírito Santo usa a Palavra para transformar corações e conformar os crentes à imagem de Cristo.",
            ],
            "citacoes": [{"texto": "Seja a minha boca cheia do teu louvor e da tua glória todo o dia.", "referencia": "Salmos 71.8"}],
            "lista_ordenada": ["Observar o texto bíblico com atenção.", "Interpretar o texto à luz do seu contexto.", "Aplicar o texto à vida concreta."],
            "lista_marcada": ["Clareza da Palavra", "Fidelidade hermenêutica", "Dependência do Espírito Santo"],
            "caixas": [{"titulo": "✦ Para reter", "texto": f"A doutrina de {titulo} é transformadora quando recebida com fé e vivida em obediência."}],
            "tabelas": [{"cabecalho": ["Elemento", "Descrição"], "linhas": [[f"{titulo} — aspecto bíblico", "Fundamentado nas Escrituras"], [f"{titulo} — aspecto prático", "Aplicado na vida diária"]]}],
            "subsecoes": [
                {"titulo": "Observação importante",
                 "paragrafos": ["É fundamental não isolar versículos fora do seu contexto imediato, literário e histórico, a fim de evitar interpretações distorcidas.", "A interpretação fiel exige oração, estudo e humildade diante do texto."],
                 "citacoes": [], "lista_ordenada": [], "lista_marcada": []},
            ],
        }

    def _translate_exception(self, e: Exception) -> None:  # pragma: no cover
        msg = str(e).lower()
        if "401" in msg or "api key not valid" in msg or "unauthenticated" in msg:
            raise GeminiAuthError(f"Falha de autenticação: {e}") from e
        if "429" in msg or "quota" in msg or "resource exhausted" in msg or "rate limit" in msg:
            raise GeminiRateLimitError(f"Quota/rate limit excedido: {e}") from e
        if "500" in msg or "503" in msg or "internal" in msg or "unavailable" in msg:
            raise GeminiServerError(f"Erro transitório do servidor: {e}") from e
        if "timeout" in msg or "connection" in msg or "reset" in msg:
            raise GeminiTransientError(f"Erro de rede/timeout: {e}") from e
        raise GeminiError(f"Erro Gemini: {e}") from e
