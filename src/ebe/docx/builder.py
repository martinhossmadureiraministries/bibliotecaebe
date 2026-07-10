"""DocumentBuilder — constrói uma apostila DOCX completa a partir de um modelo de conteúdo."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..constants import FONTE_CORPO, COR_CITACAO, HEX_PRIMARIA, HEX_LINHA_CLARA
from . import styles as S
from .styles import (
    add_horizontal_line, caixa_destaque,
    capa_completa, capitulo, citacao, configurar_estilos_base,
    h1, h2, h3, insert_logo, linhas_para_anotacoes, lista, marco_filosofico,
    novo_documento, page_break, paragrafo, selo_final, tabela,
)


@dataclass
class Secao:
    """Uma secção desenvolvida (título + parágrafos + possíveis subsecções, caixas, listas, tabelas, citações)."""
    titulo: str
    numero: Optional[str] = None
    paragrafos: list[str] = field(default_factory=list)
    citacoes: list[tuple[str, str]] = field(default_factory=list)  # (texto, ref)
    subsecoes: list["Secao"] = field(default_factory=list)
    lista_ordenada: list[str] = field(default_factory=list)
    lista_marcada: list[str] = field(default_factory=list)
    caixas: list[tuple[str, str]] = field(default_factory=list)  # (titulo, texto)
    tabelas: list[tuple[list[str], list[list[str]]]] = field(default_factory=list)  # (cabec, linhas)


@dataclass
class ExerciciosBloco:
    titulo: str
    itens: list[str] = field(default_factory=list)


@dataclass
class GlossarioEntrada:
    termo: str
    definicao: str


@dataclass
class ApostilaConteudo:
    """Modelo canónico de conteúdo de uma apostila.
    É preenchido pela camada de IA e consumido pelo DocumentBuilder."""
    # Identificação
    id_num: int
    numero: str            # "0001"
    titulo: str
    subtitulo: Optional[str] = None
    codigo: str = ""       # "EBE-APO-0001"
    instituto: str = ""
    escola: str = ""
    curso: str = ""
    modulo: str = ""
    carga_horaria: str = "25 h"
    nivel_formativo: str = ""
    autor: str = "Direcção Pedagógica · Escola Bíblica Epignósis"
    edicao_ano: str = "1.ª edição — 2026"
    revisao_pedagogica: str = "Coordenação Académica"
    revisao_doutrinaria: str = "Conselho Doutrinário"

    # Conteúdo
    apresentacao: list[str] = field(default_factory=list)
    objectivos: list[str] = field(default_factory=list)       # 4 itens: Conhecer/Crer/Viver/Servir
    versiculo_chave: tuple[str, str] = ("", "")                # (texto, referência)
    texto_base: str = ""                                       # referência de leitura
    introducao: list[str] = field(default_factory=list)
    secoes_desenvolvimento: list[Secao] = field(default_factory=list)
    aplicacao_pratica: list[str] = field(default_factory=list)
    aplicacao_itens: list[str] = field(default_factory=list)
    sintese: list[str] = field(default_factory=list)
    exercicios: list[ExerciciosBloco] = field(default_factory=list)
    estudo_complementar: dict = field(default_factory=lambda: {"titulo": "", "texto": "", "perguntas": []})
    proxima_apostila: dict = field(default_factory=lambda: {"titulo": "", "descricao": "", "preparar": []})
    glossario: list[GlossarioEntrada] = field(default_factory=list)
    bibliografia: list[str] = field(default_factory=list)


class DocumentBuilder:
    """Constrói um DOCX a partir de um `ApostilaConteudo`."""

    def __init__(self, conteudo: ApostilaConteudo):
        self.c = conteudo
        if not self.c.codigo:
            self.c.codigo = f"EBE-APO-{self.c.numero}"
        self.doc = novo_documento(f"Apostila — {self.c.titulo}", self.c.codigo)

    # ------------------------------------------------------------------
    def build(self) -> "DocumentBuilder":
        self._capa()
        self._marco_filosofico()
        self._ficha_tecnica()
        self._sumario()
        self._apresentacao()
        self._objectivos()
        self._versiculo_chave()
        self._texto_base()
        self._introducao()
        self._desenvolvimento()
        self._aplicacao()
        self._sintese()
        self._exercicios()
        self._estudo_complementar()
        self._proxima()
        self._glossario()
        self._bibliografia()
        self._anotacoes()
        self._selo()
        return self

    def save(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(p)
        return p

    # ------------------------------------------------------------------
    def _capa(self):
        capa_completa(
            self.doc,
            instituto=self.c.instituto,
            escola=self.c.escola,
            curso=self.c.curso,
            modulo=self.c.modulo,
            numero_apostila=self.c.numero.lstrip("0") or "0",
            titulo=self.c.titulo,
            subtitulo=self.c.subtitulo,
            carga_horaria=self.c.carga_horaria,
            nivel_formativo=self.c.nivel_formativo,
            autor=self.c.autor,
            edicao_ano=self.c.edicao_ano,
            codigo=self.c.codigo,
        )

    def _marco_filosofico(self):
        marco_filosofico(self.doc)

    def _ficha_tecnica(self):
        h1(self.doc, "Ficha Técnica")
        paragrafo(self.doc,
            "Este material didáctico é propriedade intelectual da Escola Bíblica "
            "Epignósis (EBE), produzido para uso exclusivo no âmbito dos seus "
            "programas de formação. A sua reprodução, no todo ou em parte, "
            "depende de autorização institucional escrita.")
        itens = [
            f"Título da apostila: {self.c.titulo}.",
            f"Curso: {self.c.curso}.",
            f"Módulo: {self.c.modulo}.",
            f"Autor / Docente: {self.c.autor}.",
            f"Revisão pedagógica: {self.c.revisao_pedagogica}.",
            f"Revisão doutrinária: {self.c.revisao_doutrinaria}.",
            "Versão bíblica de referência: Almeida Revista e Corrigida (ARC).",
            f"Edição: {self.c.edicao_ano}.",
            f"Código institucional: {self.c.codigo}.",
        ]
        lista(self.doc, itens)
        citacao(self.doc,
            "Toda a Escritura é divinamente inspirada e proveitosa para ensinar, "
            "para redarguir, para corrigir, para instruir em justiça; para que o "
            "homem de Deus seja perfeito e perfeitamente instruído para toda a boa obra.",
            "2 Timóteo 3.16-17")
        page_break(self.doc)

    def _sumario(self):
        h1(self.doc, "Sumário")
        itens = ["Apresentação da apostila",
                 "Objectivos de aprendizagem",
                 "Versículo-chave",
                 "Texto-base para leitura"]
        # Introdução + seções desenvolvimento
        itens.append("1. Introdução")
        # Desenvolvimento
        itens.append("2. Desenvolvimento do conceito central")
        for i, sec in enumerate(self.c.secoes_desenvolvimento, 1):
            num = f"2.{i}"
            itens.append(f"   {num} {sec.titulo}")
        itens.append("3. Aplicação prática")
        itens.append("4. Síntese e conclusão")
        itens.append("Exercícios de revisão")
        if self.c.estudo_complementar.get("titulo"):
            itens.append(f"Estudo bíblico complementar — {self.c.estudo_complementar['titulo']}")
        itens.append("Para a próxima apostila")
        itens.append("Glossário")
        itens.append("Bibliografia recomendada")
        itens.append("Anotações pessoais")
        lista(self.doc, itens)
        page_break(self.doc)

    def _apresentacao(self):
        h1(self.doc, "Apresentação da Apostila")
        for p in self.c.apresentacao:
            paragrafo(self.doc, p)

    def _objectivos(self):
        h1(self.doc, "Objectivos de Aprendizagem")
        paragrafo(self.doc, "Ao concluir o estudo desta apostila, o(a) aluno(a) será capaz de:")
        if self.c.objectivos:
            lista(self.doc, self.c.objectivos, ordenada=True)
        else:
            lista(self.doc, [
                "CONHECER — identificar os principais conceitos, textos e referências bíblicas relacionados ao tema.",
                "CRER — interiorizar a verdade bíblica estudada, de modo que ela transforme a sua cosmovisão.",
                "VIVER — aplicar o tema à vida quotidiana, à devoção pessoal e à santidade.",
                "SERVIR — partilhar e ensinar o conteúdo estudado no contexto da igreja local e do ministério.",
            ], ordenada=True)

    def _versiculo_chave(self):
        h1(self.doc, "Versículo-Chave")
        texto, ref = self.c.versiculo_chave
        if texto:
            citacao(self.doc, texto, ref)
        else:
            citacao(self.doc,
                "Procura apresentar-te a Deus aprovado, como obreiro que não tem de "
                "que se envergonhar, que maneja bem a palavra da verdade.",
                "2 Timóteo 2.15")

    def _texto_base(self):
        h1(self.doc, "Texto-Base para Leitura")
        if self.c.texto_base:
            paragrafo(self.doc,
                "Antes de iniciar o estudo, leia atentamente, em sua Bíblia "
                "(Almeida Revista e Corrigida), a seguinte passagem:")
            p = self.doc.add_paragraph()
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.shared import Pt
            from ..constants import COR_SECUNDARIA, FONTE_TITULO
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(self.c.texto_base)
            r.font.name = FONTE_TITULO
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = COR_SECUNDARIA
        else:
            paragrafo(self.doc,
                "Antes de iniciar o estudo, reserve um momento de oração e leia "
                "as passagens bíblicas que serão mencionadas ao longo da apostila, "
                "utilizando a versão Almeida Revista e Corrigida (ARC).")
        page_break(self.doc)

    def _introducao(self):
        h1(self.doc, "Introdução", numero="1")
        for p in self.c.introducao:
            paragrafo(self.doc, p)

    def _desenvolvimento(self):
        h1(self.doc, "Desenvolvimento do Conceito Central", numero="2")
        for i, sec in enumerate(self.c.secoes_desenvolvimento, 1):
            h2(self.doc, sec.titulo, numero=f"2.{i}")
            for par in sec.paragrafos:
                paragrafo(self.doc, par)
            for txt, ref in sec.citacoes:
                citacao(self.doc, txt, ref)
            if sec.lista_ordenada:
                lista(self.doc, sec.lista_ordenada, ordenada=True)
            if sec.lista_marcada:
                lista(self.doc, sec.lista_marcada, ordenada=False)
            for c_tit, c_txt in sec.caixas:
                caixa_destaque(self.doc, c_tit, c_txt)
            for head, rows in sec.tabelas:
                tabela(self.doc, head, rows)
            for sub in sec.subsecoes:
                h3(self.doc, sub.titulo)
                for par in sub.paragrafos:
                    paragrafo(self.doc, par)
                for txt, ref in sub.citacoes:
                    citacao(self.doc, txt, ref)
                if sub.lista_ordenada:
                    lista(self.doc, sub.lista_ordenada, ordenada=True)
                if sub.lista_marcada:
                    lista(self.doc, sub.lista_marcada, ordenada=False)
        page_break(self.doc)

    def _aplicacao(self):
        h1(self.doc, "Aplicação Prática", numero="3")
        for p in self.c.aplicacao_pratica:
            paragrafo(self.doc, p)
        if self.c.aplicacao_itens:
            lista(self.doc, self.c.aplicacao_itens, ordenada=True)

    def _sintese(self):
        h1(self.doc, "Síntese e Conclusão", numero="4")
        for p in self.c.sintese:
            paragrafo(self.doc, p)
        # Fechar com o versículo-chave se existir
        txt, ref = self.c.versiculo_chave
        if txt and ref:
            citacao(self.doc, txt, ref)
        page_break(self.doc)

    def _exercicios(self):
        h1(self.doc, "Exercícios de Revisão")
        if not self.c.exercicios:
            # Blocos padrão
            default = [
                ("I — Verifique a sua compreensão", [
                    "Resuma com as suas próprias palavras o conceito central desta apostila.",
                    "Quais são os principais argumentos bíblicos apresentados?",
                    "Cite pelo menos duas referências que sustentam o tema e explique-as.",
                ]),
                ("II — Reflexão pessoal", [
                    "Como este tema desafia ou conforta a sua caminhada cristã neste momento?",
                    "Que atitude prática você adoptará a partir desta semana em resposta ao que aprendeu?",
                    "Que oração você fará a Deus em resposta a este estudo?",
                ]),
                ("III — Ministério e serviço", [
                    "Como explicaria este tema a um irmão novo na fé, em linguagem simples?",
                    "Que situação concreta na sua igreja ou comunidade pode ser transformada pela aplicação deste ensino?",
                ]),
            ]
            for titulo, itens in default:
                h3(self.doc, titulo)
                lista(self.doc, itens, ordenada=True)
        else:
            for bloco in self.c.exercicios:
                h3(self.doc, bloco.titulo)
                lista(self.doc, bloco.itens, ordenada=True)

    def _estudo_complementar(self):
        ec = self.c.estudo_complementar
        if ec.get("titulo"):
            h1(self.doc, f"Estudo Bíblico Complementar — {ec['titulo']}")
            if ec.get("texto"):
                paragrafo(self.doc, ec["texto"])
            if ec.get("perguntas"):
                lista(self.doc, ec["perguntas"], ordenada=True)

    def _proxima(self):
        pa = self.c.proxima_apostila
        if pa.get("titulo"):
            h1(self.doc, "Para a Próxima Apostila")
            if pa.get("descricao"):
                paragrafo(self.doc, pa["descricao"])
            if pa.get("preparar"):
                lista(self.doc, pa["preparar"])
        page_break(self.doc)

    def _glossario(self):
        h1(self.doc, "Glossário")
        if not self.c.glossario:
            paragrafo(self.doc, "Os termos-chave utilizados nesta apostila serão consolidados no glossário geral da apostila correspondente.")
            return
        paragrafo(self.doc, "Definições breves dos termos-chave utilizados nesta apostila.")
        head = ["Termo", "Definição"]
        rows = [[g.termo, g.definicao] for g in self.c.glossario]
        tabela(self.doc, head, rows)

    def _bibliografia(self):
        h1(self.doc, "Bibliografia Recomendada")
        if not self.c.bibliografia:
            default = [
                "Bíblia Sagrada. Tradução de João Ferreira de Almeida, Revista e Corrigida.",
            ]
            lista(self.doc, default)
        else:
            lista(self.doc, self.c.bibliografia)

    def _anotacoes(self):
        h1(self.doc, "Anotações Pessoais")
        linhas_para_anotacoes(self.doc, n=12)

    def _selo(self):
        selo_final(self.doc)


# ---------------------------------------------------------------------------
# Helpers para secções capítulo (complemento ao styles.capitulo)
# ---------------------------------------------------------------------------
def capitulo(doc, numero_romano: str, titulo: str) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt
    from ..constants import FONTE_TITULO, COR_PRIMARIA, COR_SECUNDARIA
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(f"CAPÍTULO {numero_romano}")
    r.font.name = FONTE_TITULO
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COR_SECUNDARIA

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(titulo.upper())
    r.font.name = FONTE_TITULO
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = COR_PRIMARIA

    p = doc.add_paragraph()
    add_horizontal_line(p, color=HEX_PRIMARIA, size=4)


# Inclui o alias do capitulo_romano que o styles.py chama.
# O styles.py espera uma função `capitulo_romano`? Na verdade styles.py tinha
# `capitulo(doc, numero_romano, titulo)`; vamos expor esse nome também no styles.
# (Feito acima em styles.py? No nosso styles.py não existe ainda — adicionar)
