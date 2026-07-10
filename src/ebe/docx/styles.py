"""Motor de estilos EBE para python-docx.

Evolução de `_estilos.py` numa biblioteca interna, mantendo a identidade
visual do piloto (Garamond, paleta #1B3A5C/#2E7D4F/#C9A14B, justificado).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from ..constants import (
    COR_BRANCO, COR_CITACAO, COR_LINHA, COR_PRIMARIA, COR_SECUNDARIA,
    COR_TERCIARIA, COR_TEXTO, FONTE_CORPO, FONTE_TITULO, HEX_CINZA_CLARO,
    HEX_LINHA_CLARA, HEX_PRIMARIA, HEX_SECUNDARIA, LEMA, MARGIN_BOTTOM,
    MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARCO_FILOSOFICO, CITA_EFESIOS, SELO,
)

# Caminhos para assets
ASSETS_DIR = Path(__file__).resolve().parents[3] / "assets"
LOGO_PATH = ASSETS_DIR / "logo_ebe.png"
LOGO_PEQUENO = ASSETS_DIR / "logo_pequeno.png"
LOGO_EMBLEMA = ASSETS_DIR / "logo_emblema.png"
LOGO_MARCA_DAGUA = ASSETS_DIR / "logo_marca_dagua.png"

# Fallback retrocompatível com o layout antigo (raiz do repo / _assets)
if not LOGO_PATH.exists():
    ASSETS_DIR = Path(__file__).resolve().parents[3] / "_assets"
    LOGO_PATH = ASSETS_DIR / "logo_ebe.png"
    LOGO_PEQUENO = ASSETS_DIR / "logo_pequeno.png"
    LOGO_EMBLEMA = ASSETS_DIR / "logo_emblema.png"
    LOGO_MARCA_DAGUA = ASSETS_DIR / "logo_marca_dagua.png"


# ---------------------------------------------------------------------------
# Helpers low-level
# ---------------------------------------------------------------------------

def _set_cell_border(cell, **kwargs) -> None:
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        if edge in kwargs:
            border = OxmlElement(f"w:{edge}")
            cfg = kwargs[edge]
            border.set(qn("w:val"), cfg.get("val", "single"))
            border.set(qn("w:sz"), str(cfg.get("sz", 4)))
            border.set(qn("w:color"), cfg.get("color", "B8B8B8"))
            tcBorders.append(border)
    tcPr.append(tcBorders)


def shade_cell(cell, hex_color: str) -> None:
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_horizontal_line(paragraph, color: str = HEX_PRIMARIA, size: int = 8) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def set_page(section, top=MARGIN_TOP, bottom=MARGIN_BOTTOM,
             left=MARGIN_LEFT, right=MARGIN_RIGHT) -> None:
    section.top_margin = Cm(top)
    section.bottom_margin = Cm(bottom)
    section.left_margin = Cm(left)
    section.right_margin = Cm(right)


def page_break(doc) -> None:
    p = doc.add_paragraph()
    run = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._r.append(br)


def insert_logo(doc, caminho: Optional[os.PathLike] = None,
                largura_cm: float = 5.5, alinhamento: str = "center") -> None:
    caminho = caminho or LOGO_PATH
    p = doc.add_paragraph()
    p.alignment = {
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
    }.get(alinhamento, WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run()
    r.add_picture(str(caminho), width=Cm(largura_cm))


# ---------------------------------------------------------------------------
# Configuração global do documento
# ---------------------------------------------------------------------------

def configurar_estilos_base(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.name = FONTE_CORPO
    style.font.size = Pt(12)
    style.font.color.rgb = COR_TEXTO
    pf = style.paragraph_format
    pf.space_after = Pt(6)
    pf.space_before = Pt(0)
    pf.line_spacing = 1.4
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for section in doc.sections:
        section.page_height = Cm(29.7)
        section.page_width = Cm(21.0)
        set_page(section)


def cabecalho_rodape(doc: Document, titulo_doc: str, codigo_doc: str) -> None:
    for section in doc.sections:
        section.different_first_page_header_footer = True

        header = section.header
        ph = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        ph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        ph.text = ""
        r = ph.add_run(f"Escola Bíblica Epignósis  ·  {titulo_doc}")
        r.font.name = FONTE_TITULO
        r.font.size = Pt(9)
        r.font.italic = True
        r.font.color.rgb = COR_SECUNDARIA

        footer = section.footer
        pf = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = pf.add_run(f"{codigo_doc}  ·  ")
        r.font.name = FONTE_CORPO
        r.font.size = Pt(9)
        r.font.color.rgb = COR_CITACAO

        run = pf.add_run()
        fldChar1 = OxmlElement("w:fldChar")
        fldChar1.set(qn("w:fldCharType"), "begin")
        instrText = OxmlElement("w:instrText")
        instrText.set(qn("xml:space"), "preserve")
        instrText.text = "PAGE"
        fldChar2 = OxmlElement("w:fldChar")
        fldChar2.set(qn("w:fldCharType"), "end")
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)
        run.font.name = FONTE_CORPO
        run.font.size = Pt(9)
        run.font.color.rgb = COR_CITACAO


def novo_documento(titulo_doc: str, codigo_doc: str) -> Document:
    doc = Document()
    configurar_estilos_base(doc)
    cabecalho_rodape(doc, titulo_doc, codigo_doc)
    return doc


# ---------------------------------------------------------------------------
# Blocos estruturais
# ---------------------------------------------------------------------------

def h1(doc, texto: str, numero: Optional[str] = None) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    txt = f"{numero}. {texto}" if numero else texto
    r = p.add_run(txt.upper())
    r.font.name = FONTE_TITULO
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = COR_PRIMARIA
    add_horizontal_line(p, color=HEX_PRIMARIA, size=6)


def h2(doc, texto: str, numero: Optional[str] = None) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    txt = f"{numero} {texto}" if numero else texto
    r = p.add_run(txt)
    r.font.name = FONTE_TITULO
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = COR_PRIMARIA


def h3(doc, texto: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(texto)
    r.font.name = FONTE_TITULO
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = COR_SECUNDARIA


def paragrafo(doc, texto: str, italic: bool = False, bold: bool = False,
              justify: bool = True, indent_first: bool = False) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if justify else WD_ALIGN_PARAGRAPH.LEFT
    if indent_first:
        p.paragraph_format.first_line_indent = Cm(0.8)
    r = p.add_run(texto)
    r.font.name = FONTE_CORPO
    r.font.size = Pt(12)
    r.font.italic = italic
    r.font.bold = bold


def citacao(doc, texto: str, referencia: Optional[str] = None) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(1.5)
    p.paragraph_format.right_indent = Cm(1.0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(f"\u201C{texto}\u201D")
    r.font.name = FONTE_CORPO
    r.font.size = Pt(11)
    r.font.italic = True
    r.font.color.rgb = COR_CITACAO
    if referencia:
        r2 = p.add_run(f"  ({referencia}, ARC)")
        r2.font.name = FONTE_CORPO
        r2.font.size = Pt(10)
        r2.font.italic = True
        r2.font.color.rgb = COR_SECUNDARIA


def lista(doc, itens: list[str], ordenada: bool = False,
          recuo: float = 0.8, deslocamento: float = -0.5) -> None:
    for i, item in enumerate(itens, 1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(recuo)
        p.paragraph_format.first_line_indent = Cm(deslocamento)
        p.paragraph_format.space_after = Pt(2)
        marca = f"{i}. " if ordenada else "\u2022  "
        r = p.add_run(marca)
        r.font.name = FONTE_TITULO
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COR_SECUNDARIA
        r2 = p.add_run(item)
        r2.font.name = FONTE_CORPO
        r2.font.size = Pt(12)


def caixa_destaque(doc, titulo: str, texto: str,
                   fundo: str = HEX_CINZA_CLARO,
                   cor_titulo: RGBColor = COR_SECUNDARIA) -> None:
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    shade_cell(cell, fundo)
    _set_cell_border(
        cell,
        top={"val": "single", "sz": 4, "color": HEX_SECUNDARIA},
        left={"val": "single", "sz": 12, "color": HEX_SECUNDARIA},
        bottom={"val": "single", "sz": 4, "color": HEX_SECUNDARIA},
        right={"val": "single", "sz": 4, "color": HEX_SECUNDARIA},
    )
    # Apaga o parágrafo vazio inicial da célula e adiciona conteúdo
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(f"\u2726 {titulo}  ")
    r.font.bold = True
    r.font.color.rgb = cor_titulo
    r.font.name = FONTE_TITULO
    r.font.size = Pt(11)
    r2 = p.add_run(texto)
    r2.font.name = FONTE_CORPO
    r2.font.size = Pt(11)
    r2.font.italic = True
    doc.add_paragraph()  # respiro


def tabela(doc, cabecalho: list[str], linhas: list[list[str]],
           col_widths_cm: Optional[list[float]] = None) -> None:
    tbl = doc.add_table(rows=1, cols=len(cabecalho))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = tbl.rows[0].cells
    for i, t in enumerate(cabecalho):
        hdr[i].text = ""
        shade_cell(hdr[i], HEX_PRIMARIA)
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        r.font.bold = True
        r.font.name = FONTE_TITULO
        r.font.size = Pt(10)
        r.font.color.rgb = COR_BRANCO
    for row_data in linhas:
        row = tbl.add_row().cells
        for i, v in enumerate(row_data):
            row[i].text = str(v)
            for p in row[i].paragraphs:
                for r in p.runs:
                    r.font.name = FONTE_CORPO
                    r.font.size = Pt(10)
    if col_widths_cm:
        for i, w in enumerate(col_widths_cm):
            for row in tbl.rows:
                row.cells[i].width = Cm(w)
    doc.add_paragraph()


def selo_final(doc) -> None:
    doc.add_paragraph()
    p = doc.add_paragraph()
    add_horizontal_line(p, color=HEX_SECUNDARIA, size=4)
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ESCOLA B\u00cdBLICA EPIGN\u00d3SIS")
    r.font.name = FONTE_TITULO
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COR_PRIMARIA
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(LEMA)
    r.font.name = FONTE_TITULO
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = COR_SECUNDARIA
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Soli Deo Gloria")
    r.font.name = FONTE_TITULO
    r.font.size = Pt(9)
    r.font.italic = True
    r.font.color.rgb = COR_CITACAO


def linhas_para_anotacoes(doc, n: int = 12) -> None:
    for _ in range(n):
        p = doc.add_paragraph()
        add_horizontal_line(p, color=HEX_LINHA_CLARA, size=4)


def capitulo(doc, numero_romano: str, titulo: str) -> None:
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


# ---------------------------------------------------------------------------
# Blocos compostos (reutilizados pelo DocumentBuilder)
# ---------------------------------------------------------------------------

def capa_completa(doc, instituto: str, escola: str, curso: str,
                  modulo: str, numero_apostila: str, titulo: str,
                  subtitulo: Optional[str] = None,
                  carga_horaria: str = "2 horas de estudo",
                  nivel_formativo: str = "Nível 2 \u2014 Crescimento (Ser)",
                  autor: str = "Direcção Pedagógica \u00b7 Escola Bíblica Epignósis",
                  edicao_ano: str = "1.\u00aa edição \u2014 2026",
                  codigo: str = "EBE-APO-0001") -> None:
    doc.add_paragraph()
    insert_logo(doc, LOGO_PATH, largura_cm=5.5)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(LEMA)
    r.font.name = FONTE_TITULO
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = COR_SECUNDARIA

    p = doc.add_paragraph()
    add_horizontal_line(p, color=HEX_SECUNDARIA, size=6)
    p.paragraph_format.space_before = Pt(4)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(instituto.upper())
    r.font.name = FONTE_TITULO
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COR_SECUNDARIA

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(f"Escola de {escola}  \u00b7  Curso \u00ab{curso}\u00bb  \u00b7  {modulo}")
    r.font.name = FONTE_CORPO
    r.font.size = Pt(10)
    r.font.color.rgb = COR_CITACAO

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"APOSTILA N.\u00ba  {numero_apostila}")
    r.font.name = FONTE_TITULO
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = COR_SECUNDARIA

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(titulo)
    r.font.name = FONTE_TITULO
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = COR_PRIMARIA

    if subtitulo:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(subtitulo)
        r.font.name = FONTE_TITULO
        r.font.size = Pt(13)
        r.font.italic = True
        r.font.color.rgb = COR_TEXTO

    doc.add_paragraph()
    doc.add_paragraph()

    tbl = doc.add_table(rows=4, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    dados = [
        ("Autor / Docente", autor),
        ("Carga horária estimada", carga_horaria),
        ("Nível formativo", nivel_formativo),
        ("Edição / Ano", edicao_ano),
    ]
    for i, (k, v) in enumerate(dados):
        row = tbl.rows[i].cells
        row[0].text = k
        row[1].text = v
        shade_cell(row[0], HEX_CINZA_CLARO)
        for pp in row[0].paragraphs:
            for rr in pp.runs:
                rr.font.bold = True
                rr.font.name = FONTE_TITULO
                rr.font.size = Pt(10)
                rr.font.color.rgb = COR_PRIMARIA
        for pp in row[1].paragraphs:
            for rr in pp.runs:
                rr.font.name = FONTE_CORPO
                rr.font.size = Pt(10)

    doc.add_paragraph()
    p = doc.add_paragraph()
    add_horizontal_line(p, color=HEX_SECUNDARIA, size=4)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"Material didáctico oficial \u00b7 Código {codigo} \u00b7 {edicao_ano[-4:]}")
    r.font.name = FONTE_CORPO
    r.font.size = Pt(9)
    r.font.color.rgb = COR_CITACAO

    page_break(doc)


def marco_filosofico(doc) -> None:
    for _ in range(6):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("MARCO FILOS\u00d3FICO")
    r.font.name = FONTE_TITULO
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COR_SECUNDARIA

    p = doc.add_paragraph()
    add_horizontal_line(p, color=HEX_SECUNDARIA, size=4)

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.left_indent = Cm(2)
    p.paragraph_format.right_indent = Cm(2)
    r = p.add_run(MARCO_FILOSOFICO)
    r.font.name = FONTE_TITULO
    r.font.size = Pt(14)
    r.font.italic = True
    r.font.color.rgb = COR_PRIMARIA

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("\u2014 Escola Bíblica Epignósis \u2014")
    r.font.name = FONTE_TITULO
    r.font.size = Pt(10)
    r.font.color.rgb = COR_CITACAO

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(CITA_EFESIOS)
    r.font.name = FONTE_CORPO
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = COR_CITACAO

    page_break(doc)
