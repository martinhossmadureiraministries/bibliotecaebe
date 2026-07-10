"""Constantes institucionais e editoriais da EBE."""
from __future__ import annotations

from docx.shared import RGBColor

# ------- Cores institucionais (paleta oficial) -------
COR_PRIMARIA = RGBColor(0x1B, 0x3A, 0x5C)   # azul-marinho
COR_SECUNDARIA = RGBColor(0x2E, 0x7D, 0x4F) # verde
COR_TERCIARIA = RGBColor(0xC9, 0xA1, 0x4B)  # dourado
COR_TEXTO = RGBColor(0x1A, 0x1A, 0x1A)
COR_LINHA = RGBColor(0xB8, 0xB8, 0xB8)
COR_CITACAO = RGBColor(0x55, 0x55, 0x55)
COR_BRANCO = RGBColor(0xFF, 0xFF, 0xFF)

HEX_PRIMARIA = "1B3A5C"
HEX_SECUNDARIA = "2E7D4F"
HEX_TERCIARIA = "C9A14B"
HEX_CINZA_CLARO = "E8F1EC"   # fundo de caixas de destaque / tabela
HEX_LINHA_CLARA = "C8C8C8"

# ------- Tipografia -------
FONTE_TITULO = "Garamond"
FONTE_CORPO = "Garamond"
FONTE_MONO = "Consolas"

# ------- Dimensões (cm) -------
MARGIN_TOP = 2.5
MARGIN_BOTTOM = 2.5
MARGIN_LEFT = 3.0
MARGIN_RIGHT = 2.5

# ------- Marcas institucionais -------
LEMA = "Conhecer a Deus. Viver a Palavra. Manifestar o Reino."
CITA_EFESIOS = (
    "\"Até que todos cheguemos à unidade da fé e ao pleno conhecimento "
    "(ἐπίγνωσις) do Filho de Deus, a homem perfeito, à medida da estatura "
    "completa de Cristo.\" Efésios 4.13"
)
MARCO_FILOSOFICO = (
    "\"Acreditamos que o verdadeiro conhecimento de Deus transforma a mente "
    "pela verdade das Escrituras, o coração pela acção do Espírito Santo e "
    "a vida pelo compromisso de viver e anunciar o Evangelho de Jesus Cristo.\""
)
SELO = "Soli Deo Gloria"

# ------- Limites de produção -------
PAGINAS_MIN = 15
PAGINAS_MAX = 20
APOSTILAS_POR_DIA = 11
MAX_TENTATIVAS_GERACAO = 3
MAX_TENTATIVAS_ORIGINALIDADE = 3
LIMIAR_SIMILARIDADE = 0.70
LIMIAR_SIMILARIDADE_ESTRUTURA = 0.78
