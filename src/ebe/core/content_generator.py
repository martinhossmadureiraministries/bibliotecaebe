"""Geração de conteúdo: chama Gemini com os templates e constrói ApostilaConteudo."""
from __future__ import annotations

import json
import logging
from typing import Optional

from ..ai import prompts
from ..ai.gemini_client import GeminiClient
from ..ai.originality import OriginalityChecker
from ..config import Config
from ..curriculum.models import ApostilaInfo
from ..docx.builder import ApostilaConteudo, ExerciciosBloco, GlossarioEntrada, Secao
from ..exceptions import InvalidResponseError

log = logging.getLogger("ebe.content")


class ContentGenerator:
    def __init__(self, cfg: Config, client: GeminiClient,
                 originality: Optional[OriginalityChecker] = None):
        self.cfg = cfg
        self.client = client
        self.originality = originality
        self.system = prompts.render("system_instruction.j2")

    def generate(self, a: ApostilaInfo, total_apostilas: int = 1029,
                 attempts: int = 3) -> ApostilaConteudo:
        # Em modo simulado não precisa de tentativas; em real, com tentativas de originalidade
        for attempt in range(1, attempts + 1):
            outline = self._request_outline(a, total_apostilas)
            try:
                conteudo = self._build_from_outline(a, outline, total_apostilas)
                if self.originality:
                    txt_blob = " ".join(
                        outline.get("subtitulo", "")
                        + " ".join(outline.get("apresentacao", []))
                        + " ".join(outline.get("introducao", []))
                        + " ".join(outline.get("sintese", []))
                    )
                    self.originality.assert_original(
                        txt_blob,
                        limiar=self.cfg.geral.limiar_similaridade_estrutura,
                        contexto=f"outline ap {a.id} (tent {attempt})",
                    )
                return conteudo
            except Exception as e:
                log.warning("Tentativa %s falhou: %s", attempt, e)
                if attempt == attempts:
                    raise
        raise InvalidResponseError("Falha ao gerar conteúdo após todas as tentativas")

    def _request_outline(self, a: ApostilaInfo, total: int) -> dict:
        prompt = prompts.render("generate_outline.j2", a=a, total_apostilas=total)
        resp = self.client.generate(prompt, system_instruction=self.system,
                                     max_tokens=8192, temperature=0.7)
        return self._parse_json(resp.text)

    def _build_from_outline(self, a: ApostilaInfo, outline: dict, total: int) -> ApostilaConteudo:
        nivel_label = f"Nível {a.nivel_id} — {a.nivel}"
        # Nível formatado legível
        c = ApostilaConteudo(
            id_num=a.id,
            numero=a.numero,
            titulo=a.titulo,
            subtitulo=outline.get("subtitulo"),
            codigo=a.codigo,
            instituto=a.instituto,
            escola=a.escola,
            curso=a.curso,
            modulo=a.modulo,
            carga_horaria=a.carga_horaria or "25 h",
            nivel_formativo=nivel_label,
            apresentacao=outline.get("apresentacao", []),
            objectivos=outline.get("objectivos", []),
            versiculo_chave=(
                outline["versiculo_chave"].get("texto", ""),
                outline["versiculo_chave"].get("referencia", ""),
            ) if "versiculo_chave" in outline else ("", ""),
            texto_base=outline.get("texto_base", ""),
            introducao=outline.get("introducao", []),
            aplicacao_pratica=outline.get("aplicacao_pratica", []),
            aplicacao_itens=outline.get("aplicacao_itens", []),
            sintese=outline.get("sintese", []),
            exercicios=[ExerciciosBloco(titulo=e.get("titulo", ""), itens=e.get("itens", []))
                        for e in outline.get("exercicios", [])],
            estudo_complementar=outline.get("estudo_complementar", {}),
            proxima_apostila=outline.get("proxima_apostila", {}),
            glossario=[GlossarioEntrada(termo=g["termo"], definicao=g["definicao"])
                       for g in outline.get("glossario", [])],
            bibliografia=outline.get("bibliografia", []),
        )

        previous_snippets: list[dict] = []
        for i, sec_o in enumerate(outline.get("secoes", []), 1):
            sec_text_prompt = prompts.render(
                "generate_section.j2",
                a=a,
                section_num=f"2.{i}",
                outline=sec_o,
                previous=previous_snippets,
            )
            sec_resp = self.client.generate(sec_text_prompt,
                                             system_instruction=self.system,
                                             max_tokens=4096,
                                             temperature=0.7)
            sec_data = self._parse_json(sec_resp.text)
            subsecoes = []
            for s in sec_data.get("subsecoes", []):
                subsecoes.append(Secao(
                    titulo=s.get("titulo", ""),
                    paragrafos=s.get("paragrafos", []),
                    citacoes=[(c["texto"], c["referencia"]) for c in s.get("citacoes", [])],
                    lista_ordenada=s.get("lista_ordenada", []),
                    lista_marcada=s.get("lista_marcada", []),
                ))
            sec = Secao(
                titulo=sec_o.get("titulo", f"Secção 2.{i}"),
                paragrafos=sec_data.get("paragrafos", []),
                citacoes=[(c["texto"], c["referencia"]) for c in sec_data.get("citacoes", [])],
                lista_ordenada=sec_data.get("lista_ordenada", []),
                lista_marcada=sec_data.get("lista_marcada", []),
                caixas=[(cx["titulo"], cx["texto"]) for cx in sec_data.get("caixas", [])],
                tabelas=[(t["cabecalho"], t["linhas"]) for t in sec_data.get("tabelas", [])],
                subsecoes=subsecoes,
            )
            c.secoes_desenvolvimento.append(sec)
            previous_snippets.append({
                "numero": f"2.{i}",
                "titulo": sec.titulo,
                "snippet": " ".join(sec.paragrafos)[:200],
            })
        return c

    def _parse_json(self, text: str) -> dict:
        # Limpa o texto — por vezes os modelos envolvem em ```json
        t = text.strip()
        if t.startswith("```"):
            # remove primeira e última linha
            lines = t.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            t = "\n".join(lines)
        try:
            return json.loads(t)
        except json.JSONDecodeError as e:
            raise InvalidResponseError(f"Resposta não é JSON válido: {e}. Início: {t[:200]!r}")
