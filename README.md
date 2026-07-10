# 📚 Escola Bíblica Epignósis — Sistema de Geração de Apostilas

**Status:** Em desenvolvimento (Fase 1/5 concluída)

## Visão Geral

Sistema totalmente automatizado para gerar e publicar **1.029 apostilas** de formação bíblica em português europeu, com integração Google Gemini AI, verificação de originalidade e workflows GitHub Actions.

### Características Principais

- ✅ **Documentos institucionais completos** (identidade, fé, pedagogia, regimentos, manuais)
- ✅ **Motor DOCX modular** (`src/ebe/docx/`) com estilos académicos harmonizados
- ✅ **Currículo estruturado** (1.029 apostilas em JSON)
- 🚀 **Pipeline AI em desenvolvimento** com Gemini 1.5 Pro
- 🔒 **Verificação de originalidade** por embeddings
- 📊 **Observabilidade** em tempo real (PROJECT_STATE, CHANGELOG, ROADMAP)
- 🔄 **Workflows GitHub Actions** prontos para activação

## 📁 Estrutura do Projeto

```
bibliotecaebe/
├── src/ebe/                          # Package Python principal
│   ├── __init__.py                   # Inicialização
│   ├── cli.py                        # Interface de linha de comando
│   ├── config.py                     # Configuração centralizada
│   ├── logging_config.py             # Logging estruturado
│   ├── exceptions.py                 # Exceções customizadas
│   ├── docx/                         # Geração de documentos Word
│   │   ├── __init__.py
│   │   └── styles.py                 # Estilos académicos EBE
│   ├── ai/                           # (M2) Integração Gemini
│   ├── curriculum/                   # (M3) Modelo do currículo
│   ├── core/                         # (M3) Pipeline principal
│   └── registry/                     # (M3) Registro de geração
├── state/                            # Estado e configuração
│   ├── curriculum.json               # Mapa de 1.029 apostilas
│   ├── registry.jsonl                # Registro de geradas
│   └── last_error.json               # Último erro (diagnostics)
├── output/                           # Apostilas geradas (.docx)
├── docs/                             # Documentação técnica
│   ├── PLANO_ARQUITETURA.md
│   ├── GEMINI_SETUP.md
│   └── ...
├── .github/workflows/                # (após activação) Workflows CI/CD
├── _assets/                          # Logotipos e recursos visuais
├── LEIA-ME.md                        # Especificação dos documentos
├── PROJECT_STATE.md                  # Estado actual do pipeline
├── ROADMAP.md                        # Plano de desenvolvimento
└── requirements.txt                  # Dependências Python
```

## 🚀 Quick Start

### 1. Instalação

```bash
# Clone ou navigate to repo
cd bibliotecaebe

# Install dependencies
pip install -r requirements.txt

# Initialize project
python -m ebe init
```

### 2. Configurar API Gemini (obrigatório para M2+)

```bash
# Siga o guia: docs/GEMINI_SETUP.md
# Resumo: crie chave gratuita em Google AI Studio, adicione como GitHub Secret
```

### 3. Activar Workflows

```bash
# Mova workflows de workflows_ready/ para .github/workflows/
cp workflows_ready/*.yml .github/workflows/
```

### 4. Testar Localmente (M1)

```bash
# Gera exemplo (simula sem API Gemini)
python -m ebe generate --count 1
```

## 📋 Marcos de Desenvolvimento

| Marco | Objetivo | Status | Prazo |
|-------|----------|--------|-------|
| M0 | Plano de arquitectura | ✅ | Concluído |
| M1 | Refactoring motor DOCX | ✅ | ✅ Jul 2026 |
| M2 | Cliente Gemini + prompts | ⏳ | Próximo |
| M3 | Pipeline core + checkpoint | ⏳ | ~2 semanas |
| M4 | Verificador de originalidade | ⏳ | ~3 semanas |
| M5 | Workflows GitHub Actions | ⏳ | ~4 semanas |
| M6 | Observabilidade auto | ⏳ | ~5 semanas |
| M7 | Primeiro lote (11 apostilas) | ⏳ | ~6 semanas |
| M8 | Produção contínua (11/dia) | ⏳ | ~10-12 semanas |
| M9 | Extensão a outros formatos | ⏳ | ~14 semanas |

## 📚 Documentação

- **[LEIA-ME.md](LEIA-ME.md)** — Especificação completa dos documentos institucionais
- **[PROJECT_STATE.md](PROJECT_STATE.md)** — Estado actual da geração (atualizado automaticamente)
- **[ROADMAP.md](ROADMAP.md)** — Plano detalhado dos próximos marcos
- **[docs/PLANO_ARQUITETURA.md](docs/PLANO_ARQUITETURA.md)** — Arquitectura técnica
- **[docs/GEMINI_SETUP.md](docs/GEMINI_SETUP.md)** — Guia de configuração Gemini

## 🔧 Dependências

- Python 3.11+
- `python-docx` — Geração de documentos
- `google-generativeai` — API Gemini
- `jinja2` — Templates para prompts
- `pydantic` — Validação de dados
- `tenacity` — Retry com backoff exponencial
- `click` — CLI

Ver [requirements.txt](requirements.txt) para versões pinadas.

## 🔐 Segurança

- **Chave API:** Armazenada como GitHub Secret, nunca em git
- **Rate limiting:** Modo simulate para testes (sem API)
- **Logs:** Estruturados em JSON, sem dados sensíveis
- **CORS:** Workflows rodamlocalmente ou em GitHub Actions

Ver [SECURITY.md](SECURITY.md) para política completa.

## 📞 Suporte

- **Issues:** Use GitHub Issues para bugs e feature requests
- **Discussões:** GitHub Discussions para ideias e Q&A
- **Documentação:** Consulte `docs/`

## 📄 Licença

Escola Bíblica Epignósis — Sistema Proprietário (2026)

---

**Soli Deo Gloria** 🙏
