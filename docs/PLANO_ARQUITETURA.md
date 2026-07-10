# PLANO DE ARQUITETURA · SISTEMA DE GERAÇÃO DE APOSTILAS EBE
> Versão 1.0 — 2026-07-10 · Equipa: Arquiteto Sénior + IA + DevOps + Qualidade

**Escola Bíblica Epignósis (EBE)** · Plataforma de produção automatizada de materiais didáticos.

---

## 1. VISÃO GERAL

Construir uma **plataforma profissional, escalável e segura** para gerar automaticamente, com qualidade editorial de livro e 100% de originalidade, as **1.029 apostilas oficiais** da EBE via API gratuita do Google Gemini, em DOCX editável, com pipeline de CI/CD no GitHub Actions, controlo total de qualidade, rastreabilidade e capacidade de evoluir para livros, e-books, avaliações, planos de aula, apresentações e outros materiais.

### 1.1 Princípios norteadores

| # | Princípio | Descrição |
|---|-----------|-----------|
| P1 | **Originalidade máxima** | Nenhuma reutilização de capítulos, exemplos, exercícios, perguntas ou conclusões entre apostilas. |
| P2 | **Fidelidade curricular** | Seguir rigidamente `state/curriculum.json`. Nunca alterar títulos, módulos, cursos ou ordem. |
| P3 | **Qualidade editorial** | Saída equivalente a livro profissional: capa, índice, cabeçalhos, rodapés, paginação, tipografia Garamond, paleta EBE. |
| P4 | **Respeito aos limites da API** | Rate limiting, filas, retry com backoff exponencial, retomada automática. |
| P5 | **Idempotência** | Nunca regenerar uma apostila já finalizada; o pipeline é sempre retomável do ponto exacto onde parou. |
| P6 | **Rastreabilidade total** | Registo permanente (ID, título, data, versão, hash, commit, status, prompts usados). |
| P7 | **Modularidade (SOLID/DRY/KISS)** | Componentes pequenos, reutilizáveis, testáveis, com responsabilidade única. |
| P8 | **Segurança** | Chave Gemini apenas em GitHub Secrets; nunca em código, logs ou commits. |
| P9 | **Evolução contínua** | Arquitetura preparada para novos tipos de material e novos mapas curriculares. |

### 1.2 Conflito de branches (nota prévia)
A sessão foi aberta pelo Arena na branch `arena/019f4b1b-bibliotecaebe` (regra do sistema que não pode ser contornada neste ambiente). O trabalho técnico será realizado nessa branch, com histórico linear, sem PRs internos desnecessários. No final de cada marco validado, **você mesmo (no telemóvel)** poderá fazer o merge para `main` com um comando; darei o procedimento passo a passo.


## 2. ARQUITETURA DO SISTEMA

### 2.1 Visão em camadas

```
┌──────────────────────────────────────────────────────────────────────────┐
│  6. Camada de Apresentação / Operação                                    │
│     • GitHub Actions (workflows)  • CLI local  • PROJECT_STATE.md        │
├──────────────────────────────────────────────────────────────────────────┤
│  5. Camada de Orquestração                                               │
│     • Pipeline Generator (scheduler, fila, retomada, rate-limit)         │
├──────────────────────────────────────────────────────────────────────────┤
│  4. Camada de Geração de Conteúdo (IA)                                   │
│     • Gemini Client  • Prompt Builder  • Context Caching  • Verificador  │
│       de originalidade/similaridade  • Validador teológico-estrutural    │
├──────────────────────────────────────────────────────────────────────────┤
│  3. Camada de Renderização DOCX                                          │
│     • Motor de estilos EBE (_estilos evoluído)  • Template de apostila   │
│       • Construtor de secções  • Índice automático  • Paginação          │
├──────────────────────────────────────────────────────────────────────────┤
│  2. Camada de Persistência / Estado                                      │
│     • state/curriculum.json  • state/registry.jsonl  • state/logs/*.log  │
│       • state/hashes/*.sha256  • output/apostilas/*.docx                 │
├──────────────────────────────────────────────────────────────────────────┤
│  1. Camada de Base e Utilitários                                         │
│     • Config  • Logging  • Exceptions  • RateLimiter  • Hash  • Retry    │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Padrão arquitetural

- **Pipeline + Fila (Queue-based worker)**. Cada apostila é uma unidade de trabalho (job).
- **Template Method** para o fluxo de geração de cada apostila.
- **Strategy** para diferentes tipos de material futuro (apostila, livro, avaliação, plano de aula, etc.), através de um `Renderer` e um `PromptBuilder` plugáveis.
- **Repository pattern** para leitura/escrita do estado (permite futuramente trocar JSON por SQLite/PostgreSQL sem tocar no pipeline).
- **Result Object pattern** para erros (sem exceções silenciosas; tudo é registado em logs e no estado).


## 3. ESTRUTURA DO REPOSITÓRIO

```
bibliotecaebe/
│
├── README.md                           # Apresentação pública do projeto
├── LEIA-ME.md                          # (existente) resumo dos documentos institucionais
├── CONTRIBUTING.md                     # Guia de contribuição
├── SECURITY.md                         # Política de segurança (chaves, secrets)
├── CHANGELOG.md                        # Histórico técnico automático
├── ROADMAP.md                          # Estado do projecto (concluído/andamento/próximos)
├── PROJECT_STATE.md                    # Painel de estado auto-atualizado
├── VERSION                             # Versão semântica do sistema (ex: 0.1.0)
├── requirements.txt                    # Dependências Python
├── pyproject.toml                      # Configuração do pacote e ferramentas
│
├── docs/                               # Documentação do projecto
│   ├── PLANO_ARQUITETURA.md            # ESTE FICHEIRO
│   ├── MANUAL_CRIACAO_MAPAS.md         # Manual para futuros mapas curriculares
│   ├── GEMINI_SETUP.md                 # Guia passo-a-passo (telemóvel) p/ chave API
│   ├── PROMPTS.md                      # Documentação dos blocos de prompt
│   ├── EDITORIAL_STYLE_GUIDE.md        # Guia de estilo editorial
│   └── TROUBLESHOOTING.md              # Resolução de problemas comuns
│
├── assets/                             # Recursos estáticos (logos, fontes)
│   ├── logo_ebe.png                    # (já existentes; link simbólico para _assets)
│   ├── logo_pequeno.png
│   ├── logo_emblema.png
│   └── logo_marca_dagua.png
│
├── src/                                # Código-fonte do sistema
│   └── ebe/
│       ├── __init__.py
│       ├── __main__.py                 # Ponto de entrada CLI (python -m ebe)
│       ├── config.py                   # Carrega settings (env + YAML)
│       ├── constants.py                # Códigos, cores, versões
│       ├── logging_setup.py            # Configuração central de logs
│       ├── exceptions.py               # Exceções tipadas
│       │
│       ├── core/
│       │   ├── pipeline.py             # Orquestração principal
│       │   ├── job.py                  # Definição de Job (unidade de trabalho)
│       │   ├── scheduler.py            # Seleciona os N jobs do dia
│       │   ├── resume.py               # Recuperação/retomada de execução
│       │   └── autodiagnostico.py      # Revisão pós-execução
│       │
│       ├── curriculum/
│       │   ├── models.py               # Dataclasses: Nivel, Instituto, Escola, Curso, Modulo, Apostila
│       │   ├── repository.py           # Leitura/consulta de curriculum.json
│       │   └── validator.py            # Valida integridade do mapa (1029, ids, etc.)
│       │
│       ├── ai/
│       │   ├── gemini_client.py        # Wrapper seguro do google-generativeai
│       │   ├── rate_limiter.py         # Token bucket p/ TPM/RPM/RPD
│       │   ├── backoff.py              # Retry com exponential backoff + jitter
│       │   ├── prompts/
│       │   │   ├── __init__.py
│       │   │   ├── system_instruction.j2
│       │   │   ├── generate_outline.j2
│       │   │   ├── generate_section.j2
│       │   │   ├── generate_exercises.j2
│       │   │   └── generate_glossary.j2
│       │   ├── context_cache.py        # Cache de system_instruction (Context Caching API)
│       │   ├── originality.py          # Comparador de similaridade (embeddings)
│       │   └── parser.py               # Validação/limpeza da resposta do modelo
│       │
│       ├── docx/
│       │   ├── styles.py               # _estilos.py evoluído (pasta dedicada)
│       │   ├── document_builder.py     # Montagem final do DOCX
│       │   ├── sections/
│       │   │   ├── capa.py
│       │   │   ├── marco_filosofico.py
│       │   │   ├── ficha_tecnica.py
│       │   │   ├── sumario.py
│       │   │   ├── apresentacao.py
│       │   │   ├── objectivos.py
│       │   │   ├── versiculo_chave.py
│       │   │   ├── texto_base.py
│       │   │   ├── capitulo.py
│       │   │   ├── secao.py
│       │   │   ├── citacao.py
│       │   │   ├── caixa_destaque.py
│       │   │   ├── tabela.py
│       │   │   ├── aplicacao.py
│       │   │   ├── sintese.py
│       │   │   ├── exercicios.py
│       │   │   ├── estudo_complementar.py
│       │   │   ├── proxima.py
│       │   │   ├── glossario.py
│       │   │   ├── bibliografia.py
│       │   │   └── anotações.py
│       │   └── fonts.py                 # Registo da Garamond (fallback)
│       │
│       ├── registry/
│       │   ├── manager.py              # Leitura/escrita do registry.jsonl
│       │   ├── hash.py                 # Cálculo/verificação de hash de conteúdo
│       │   └── models.py
│       │
│       ├── state/
│       │   ├── project_state.py        # Geração de PROJECT_STATE.md
│       │   ├── changelog.py            # Actualização de CHANGELOG.md
│       │   └── roadmap.py              # Actualização de ROADMAP.md
│       │
│       └── utils/
│           ├── fs.py
│           ├── texts.py
│           ├── bible_refs.py           # Validação leve de referências bíblicas
│           └── metrics.py              # Páginas, tokens, tempo
│
├── prompts/                            # Ficheiros .j2 usados pelo motor (cópia canónica)
│   └── (sincronizado com src/ebe/ai/prompts/ via build)
│
├── state/                              # Estado persistente do sistema
│   ├── curriculum.json                 # Mapa extraído do PDF (fonte canónica)
│   ├── curriculum.source.pdf           # PDF original de referência
│   ├── registry.jsonl                  # Registo permanente de apostilas (1 linha por apostila)
│   ├── hashes/
│   │   └── EBE-APO-NNNN_<slug>.sha256  # Hash de cada apostila gerada
│   ├── logs/
│   │   └── run-YYYYMMDD-HHMMSS.log     # Logs detalhados por execução
│   ├── embeddings/
│   │   └── EBE-APO-NNNN.npz            # Embeddings de secções para controlo de similaridade
│   ├── cache/
│   │   └── gemini_cache.json           # Referências a contextos cacheados do Gemini
│   └── last_error.json                 # Último erro (para diagnóstico rápido)
│
├── output/                             # Documentos gerados (organizados por nível/instituto)
│   └── N01/I01/<Escola>/<Curso>/
│       └── EBE-APO-NNNN_<titulo_slug>.docx
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── tools/
│   ├── parse_mapa.py                   # Parser do PDF para curriculum.json (já existe)
│   ├── rehash.py                       # Regenera hashes após mudança de motor
│   ├── repair_registry.py              # Reconstrói registry a partir dos ficheiros em output/
│   ├── local_run.py                    # Wrapper para gerar 1 apostila localmente (teste)
│   └── diag.py                         # Comando de autodiagnóstico
│
├── workflows_ready/                    # Workflows prontos (antes de mover para .github/workflows)
│   ├── daily_generate.yml              # Gera 11 apostilas/dia
│   ├── validate.yml                    # Valida estrutura e qualidade
│   ├── autodiagnostic.yml              # Revisão semanal
│   └── update_dashboard.yml            # Actualiza PROJECT_STATE/ROADMAP
│
└── .github/                            # (quando o utilizador mover os workflows)
    └── workflows/
```

> **Nota sobre `_assets` vs `assets/`:** o código actual usa `_assets/` para guardar logos. Será normalizado para `assets/` com retrocompatibilidade (um `_estilos.py` adaptador importando do novo módulo).


## 4. MÓDULOS PRINCIPAIS

### 4.1 `curriculum/` — Fonte de verdade
- Carrega `state/curriculum.json` (gerado por `tools/parse_mapa.py`).
- Valida automaticamente: 1.029 apostilas, IDs 1..1029, sem lacunas, sem duplicados, hierarquia consistente.
- Expõe métodos como `next_pending(n=11)`, `get_by_id(id)`, `list_by_level/school/course`.

### 4.2 `ai/gemini_client.py` — Cliente Gemini
- Inicialização com `google.generativeai.GenerativeModel` (modelo padrão: `gemini-2.0-flash`; raciocínio: `gemini-2.5-flash` quando necessário).
- **Rate limiting por token bucket** respeitando a cota gratuita oficial:
  - Free tier (em data de 2026): ≈ 15 RPM / 1.000.000 TPM / 1.500 RPD (modelo flash); o sistema terá valores configuráveis em `config.yaml` com fallback seguro conservador (5 RPM / 500k TPM / 1000 RPD) para evitar bloqueios.
- **Retry automático** com exponential backoff + jitter para erros 429/5xx/network.
- **Context Caching**: `system_instruction` e o guia editorial são enviados como conteúdo cacheado (`CachedContent`), reutilizado entre todas as apostilas do dia, reduzindo tokens em ~70-80%. Os conteúdos das apostilas **nunca** são cacheados entre si (P1 — originalidade).
- **Streaming opcional** para diagnóstico local.
- **Logs sem chave**: a chave é lida de `GEMINI_API_KEY` e NUNCA escrita em logs.

### 4.3 `ai/prompts/` — Construção de prompts (Jinja2)
- **Prompt de sistema (system_instruction)**: identidade institucional, doutrina, 4 eixos (Conhecer/Crer/Viver/Servir), versão ARC, joia de originalidade, proibição de plágio, tom académico-didáctico, instruções de formatação do conteúdo.
- **Prompt de outline**: gera estrutura detalhada (secções, subsecções, referências bíblicas, exercícios) da apostila, com base no título e no caminho curricular.
- **Prompt de secção**: gera o texto de cada secção (introdução, subsecções, aplicação, síntese) garantindo coerência com o outline e evitando repetições internas.
- **Prompt de exercícios**: gera 3 blocos (compreensão, reflexão, ministério) com perguntas inéditas.
- **Prompt de glossário + bibliografia**: lista terminologia e obras reais (sem invenção).
- Todos os prompts são versionados em ficheiros `.j2` e o ID do prompt + hash é gravado no `registry.jsonl` (rastreabilidade).

### 4.4 `ai/originality.py` — Controlo de similaridade
- Após gerar o outline e após gerar cada secção, calcula embeddings (via `text-embedding-004`) e compara com embeddings das apostilas anteriores.
- Se similaridade de cosseno > limiar configurável (padrão: 0,78 para estrutura, 0,70 para frases) → **regenera automaticamente** a parte afectada (máx. 3 tentativas com sementes diferentes).
- Após a geração completa do DOCX, compara também com todos os ficheiros anteriores (corpo textual extraído do .docx).
- Resultado do controlo é gravado no `registry.jsonl` (`similarity_score`, `retries`).

### 4.5 `docx/` — Renderização
- Evolução do actual `_estilos.py` para um motor modular que constrói cada secção como componente separado, todos usando a mesma identidade visual (paleta `#1B3A5C` / `#2E7D4F` / `#C9A14B`, Garamond 12pt, justificado).
- **Capa** com logo, hierarquia institucional, quadro de identificação (autor, carga horária, nível, edição).
- **Marco filosófico** obrigatório.
- **Ficha técnica** (incluindo código `EBE-APO-NNNN`, revisão pedagógica/doutrinária).
- **Sumário automático** (campo TOC do Word, preenchido pelo Word; um índice textual renderizado também é incluído como fallback).
- **Corpo** com h1/h2/h3, parágrafos justificados, citações recuadas, caixas de destaque, tabelas, listas numeradas e não numeradas.
- **Exercícios** em três blocos, **Estudo Bíblico Complementar**, **Para a próxima apostila**, **Glossário**, **Bibliografia**, **Anotações pessoais**, **Selo final**.
- **Cabeçalho e rodapé** com paginação automática (semelhante ao piloto).
- **Tamanho-alvo**: 15–20 páginas reais A4; o pipeline mede o número de páginas via contagem de quebras e densidade de conteúdo, e se ficar curto pede expansão à IA; se longo, pede condensação — nunca com quebras artificiais ou texto repetitivo.

### 4.6 `registry/` — Registo permanente
Formato de `state/registry.jsonl` (uma linha por apostila, JSON):

```json
{
  "id": 1,
  "numero": "0001",
  "codigo": "EBE-APO-0001",
  "titulo": "O Estado de Perdição do Ser Humano",
  "nivel": "Discípulo (Conhecer)",
  "instituto": "Instituto de Formação Cristã",
  "escola": "Fundamentos da Fé",
  "curso": "Salvação e Novo Nascimento",
  "modulo": "Módulo 1 — Fundamentos da Salvação",
  "carga_horaria": "25 h",
  "status": "finalizado",          # pending | generating | generated | validated | failed | regenerated
  "data_geracao": "2026-07-12T04:33:12Z",
  "versao_sistema": "0.1.0",
  "commit": "abc1234",
  "modelo_gemini": "gemini-2.0-flash",
  "prompt_hash": "sha256:...",
  "hash_arquivo": "sha256:...",
  "paginas_estimadas": 17,
  "similarity_max": 0.42,
  "retries": 0,
  "caminho_docx": "output/N01/I01/Fundamentos_da_Fe/Salvacao_e_Novo_Nascimento/EBE-APO-0001_....docx",
  "erro": null
}
```

### 4.7 `state/` — Relatórios automáticos
- **`PROJECT_STATE.md`**: painel com criadas/restantes, última apostila, próximo item, último workflow, último erro, status da API, progresso geral (barra).
- **`CHANGELOG.md`**: entradas automáticas após cada marco (marcador `<!-- AUTO:CHANGELOG -->`).
- **`ROADMAP.md`**: blocos ✅ Concluído · 🟡 Em andamento · ⏳ Próximos passos · 💡 Melhorias futuras.


## 5. FLUXO COMPLETO (ponta a ponta)

### 5.1 Fluxo diário automático (GitHub Actions)

```
[trigger: schedule 04:00 UTC diário]
        │
        ▼
1. Autenticar GH / carregar secrets.GEMINI_API_KEY
        │
        ▼
2. Autodiagnóstico rápido (integridade state/, logs recentes, cota API)
        │
        ▼
3. Ler curriculum.json + registry.jsonl → determinar próxima(s) pendente(s)
   (máx. 11 por dia, ou menos se a cota estiver baixa)
        │
        ▼
4. Para cada apostila (job), em fila sequencial:
   4.1 Reservar job (escreve "generating" no registry + commit de marcação)
   4.2 Construir outline via Gemini (com system_instruction cacheado)
   4.3 Verificar similaridade do outline vs apostilas anteriores
       ── se > limiar: regenera (máx. 3x)
   4.4 Gerar secções em blocos (apresentação, objectivos, texto-base,
       desenvolvimento 2.1..2.4, aplicação, síntese, exercícios,
       estudo complementar, glossário, bibliografia)
       ── após cada secção: verifica similaridade
   4.5 Montar DOCX com o motor editorial (capa..selo)
   4.6 Validar estrutura (todas as secções presentes, 15-20 págs,
       sem placeholders "…" ou texto genérico)
   4.7 Extrair texto, comparar similaridade global vs anteriores
       ── se alta: regenera partes necessárias
   4.8 Calcular hash, mover para output/.../ com caminho normalizado
   4.9 Escrever entrada no registry.jsonl (status=finalizado)
   4.10 Commitar artefactos (docx + state) com mensagem padronizada
        │
        ▼
5. Actualizar PROJECT_STATE.md, CHANGELOG.md, ROADMAP.md
        │
        ▼
6. Commit final + push para a branch de trabalho
        │
        ▼
7. (Futuramente) abrir PR automático para main com o lote do dia
```

### 5.2 Fluxo de retomada após falha

- Cada job tem **checkpoint** em `state/registry.jsonl` com status explícito.
- Antes de cada execução, o scheduler:
  1. Procura entradas com status `generating` e `commit` igual ao último commit do workflow interrompido → marca como `failed` e **recomeça do zero apenas esse job** (outros finalizados permanecem).
  2. Ignora entradas `finalized` e `validated`.
- Em caso de erro 429 (quota) → pausa, aguarda o tempo indicado pelo header `Retry-After`, retoma.
- Em caso de erro permanente (chave inválida, excepção não recuperável) → regista `last_error.json`, actualiza `PROJECT_STATE.md`, falha o workflow graciosamente (sem derrubar os já gerados).

### 5.3 Fluxo de validação de originalidade (diagrama textual)

```
conteúdo_gerado ──► extrair_texto ──► embedding ──┐
                                                  ├─► similaridade_cosseno
embeddings_apostilas_anteriores (state/embeddings)─┘
         │
         ├── < 0,70  → aprova
         ├── 0,70-0,78 → regenera secção afetada
         └── > 0,78  → regenera apostila inteira (máx. 3x)
```


## 6. TECNOLOGIAS E DEPENDÊNCIAS

### 6.1 Linguagem e runtime
- **Python 3.11+** (já disponível no ambiente).
- Execução em **GitHub Actions** (`ubuntu-latest`, Python setup).

### 6.2 Dependências Python (`requirements.txt`)

| Pacote | Versão | Finalidade |
|--------|--------|------------|
| `python-docx` | ≥1.1 | Geração de DOCX (já usado no projecto) |
| `google-generativeai` | ≥0.8 | Cliente oficial Gemini |
| `google-ai-generativelanguage` | ≥0.6 | Context Caching API |
| `jinja2` | ≥3.1 | Templates de prompt |
| `pyyaml` | ≥6.0 | Ficheiros de configuração |
| `tenacity` | ≥8.2 | Retry/backoff (em vez de reinventar) |
| `numpy` | ≥1.26 | Cálculo de similaridade de embeddings |
| `pdfplumber` | ≥0.11 | Leitura do PDF do mapa (apenas ferramenta) |
| `pydantic` | ≥2.0 | Validação de modelos/dados |
| `python-slugify` | ≥8.0 | Slugs de caminhos de ficheiros |
| `tqdm` | ≥4.66 | Barras de progresso local |
| `click` | ≥8.1 | CLI |

Desenvolvimento/testes: `pytest`, `pytest-cov`, `ruff`, `mypy`, `pre-commit`.

### 6.3 Serviços externos
- **Google Gemini API (free tier)** — modelo `gemini-2.0-flash` para geração, `text-embedding-004` para similaridade, `CachedContent` para contexto fixo.
- **GitHub Actions** — orquestração e execução.
- **GitHub Secrets** — armazenamento da `GEMINI_API_KEY`.

### 6.4 Sistema de ficheiros
- Apenas ficheiros no repositório (sem BD externa no início).
- Estrutura preparada para migrar para SQLite/PostgreSQL se necessário (Repository pattern).


## 7. CRONOGRAMA (faseado, incremental)

O cronograma é realista considerando o limite de **11 apostilas/dia** (≈94 dias úteis para concluir as 1.029 depois de o pipeline estar em produção). A construção do sistema vem primeiro.

| Marco | Descrição | Entregáveis | Estimativa |
|-------|-----------|-------------|------------|
| **M0** | Plano de arquitetura e base documental | `docs/PLANO_ARQUITETURA.md`, `MANUAL_CRIACAO_MAPAS.md`, `PROJECT_STATE.md`, `CHANGELOG.md`, `ROADMAP.md`, `GEMINI_SETUP.md` (esqueleto), estrutura de pastas, `requirements.txt`, `config.yaml` | Esta sessão |
| **M1** | Refatoração do motor DOCX | `src/ebe/docx/` com componentes modulares; gerar apostila piloto pelo novo motor (regressão visual) | 2-3 ciclos |
| **M2** | Cliente Gemini + prompts + rate-limiter | `gemini_client.py`, `backoff.py`, `rate_limiter.py`, prompts `.j2`; **teste local** a gerar uma apostila em sandbox com uma chave de teste | 2-3 ciclos |
| **M3** | Core do pipeline + registry + retomada | `pipeline.py`, `scheduler.py`, `registry/`, `resume.py`; geração ponta a ponta de 3 apostilas (locais) | 2 ciclos |
| **M4** | Sistema de originalidade | `originality.py`, embeddings, limiares; testes com 3 apostilas de amostra | 1-2 ciclos |
| **M5** | Workflows GitHub Actions | `workflows_ready/daily_generate.yml`, `validate.yml`, `update_dashboard.yml`; execução automática de 11 apostilas/dia no GitHub | 2 ciclos |
| **M6** | Observabilidade (logs, estado, métricas) | `PROJECT_STATE.md` automático, `CHANGELOG` automático, `last_error.json`, painel no README | 1 ciclo |
| **M7** | Produção das primeiras 11 apostilas | Primeiro lote em produção; validação editorial manual | No dia seguinte ao M5 |
| **M8** | Produção contínua | 11 apostilas/dia até concluir as 1.029 | ~94 dias corridos |
| **M9** | Extensão para outros formatos | Livros, e-books, avaliações, planos de aula (estratégia no §9) | Após M8 |


## 8. ESTRATÉGIA DE TRATAMENTO DE RISCOS

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| Esgotar cota gratuita do Gemini | M | Atraso diário | Rate limiter conservador; medir TPM/RPM/RPD em tempo real; ao aproximar do limite o workflow para e guarda o checkpoint para o dia seguinte; possibilidade de adicionar uma 2ª chave (rotação). |
| Bloqueio (429) por rácios | M | Falha intermitente | Retry com exponential backoff + jitter; respeito ao `Retry-After`; pedidos em série (não paralelos) no início. |
| Chave API exposta no repo | B | Crítico | Apenas GitHub Secrets; `.secrets` no `.gitignore`; hook pre-commit de detecção de chaves; `git-secrets` no CI; logs filtram qualquer string que pareça chave. |
| Conteúdo não original / repetitivo | M | Qualidade baixa | Embeddings de todas as apostilas anteriores + limiar de similaridade + até 3 regenerações; revisão editorial por amostragem. |
| Referências bíblicas inventadas | M | Doutrinariamente incorreto | Prompt proíbe invenção; pede só ARC; validador leve (`bible_refs.py`) com lista canónica; pós-geração: qualquer referência não reconhecida é assinalada e o parágrafo é regenerado. |
| Apostila com menos de 15 ou mais de 20 páginas | M | Má qualidade | Medição após render; se fora do intervalo: pipeline pede expansão/condensação dirigida a secções específicas (não texto genérico). |
| Falha no meio do lote diário | M | Reinício de tudo | Checkpoint por apostila; retoma do primeiro job não-finalizado. |
| Corrupção de ficheiros em `state/` | B | Perda de progresso | Validação de JSON antes de escrever; escrita atómica (escreve `.tmp` e depois `rename`); commit automático depois de cada apostila. |
| Mudança futura da API Gemini | B | Quebra do cliente | Wrapper isolado (`gemini_client.py`) é o único ponto de contacto; versões fixadas em `requirements.txt`. |
| PDF do mapa desactualizado | M | Apostilas fora da ordem | Validação do `curriculum.json` vs um checksum guardado do PDF; manual de criação de novos mapas (ver `MANUAL_CRIACAO_MAPAS.md`). |
| O utilizador usa apenas telemóvel | M | Difícil intervenção | Tudo automático; instruções do `GEMINI_SETUP.md` desenhadas para ecrã pequeno; falhas são registadas de forma legível no `PROJECT_STATE.md`. |


## 9. ESTRATÉGIA DE ESCALABILIDADE

A arquitectura já prevê crescimento:

1. **Novos tipos de material** (livros, e-books, manuais, planos de aula, apresentações, avaliações, provas, exercícios, guias de estudo, materiais institucionais):
   - Cada tipo é um **plugin** em `src/ebe/materials/<tipo>/` com `PromptBuilder` + `Renderer` próprios, registado num catálogo (`registry/material_types.py`).
   - O pipeline é agnóstico ao tipo — apenas consome jobs com um campo `material_type`.

2. **Novos mapas curriculares** (após os 1.029):
   - O sistema usa `state/curriculum.json` como interface. Basta substituir/acrescentar com um novo ficheiro e actualizar `config.yaml` (`curriculum_version`).
   - Ver manual dedicado: `docs/MANUAL_CRIACAO_MAPAS.md`.

3. **Múltiplos modelos/fornecedores de IA**:
   - O `gemini_client.py` implementa uma interface `LLMClient`; no futuro podemos adicionar `OpenAIClient`, `AnthropicClient`, etc., seleccionáveis por configuração.

4. **Paralelismo**:
   - Por enquanto sequencial (mais seguro para a cota gratuita). O `rate_limiter.py` e o padrão fila permitem ligar paralelismo controlado quando houver cota paga.

5. **Persistência**:
   - JSON/JSONL na fase inicial; camada Repository permite trocar para SQLite/PostgreSQL sem tocar no resto.

6. **Métricas e observabilidade**:
   - Preparado para exportar métricas Prometheus se em futuro houver servidor; por agora ficheiros de log + dashboard em Markdown.


## 10. ESTRATÉGIA DE RECUPERAÇÃO DE FALHAS

1. **Escrita atómica**: qualquer ficheiro de estado é escrito para `*.tmp` e depois renomeado (operação atómica em Linux).
2. **Checkpoint por apostila**: o estado de cada job é escrito ANTES do início real e ACTUALIZADO após cada passo.
3. **Logs estruturados** em JSON Lines (`state/logs/run-*.log`), com timestamps, job-id, fase.
4. **Retoma idempotente**: se o output docx existe e o hash corresponde ao registry, o job pulado.
5. **Backup automático via Git**: cada apostila é commitada; em qualquer altura é possível `git revert` para um estado funcional anterior. Antes de alterações críticas (refactors, mudanças de prompt), é criado um **tag** semântico (`v0.1.0-pre-m1`, etc.).
6. **Falha de API**: o cliente tem três níveis de retry (erros transitórios, quota baixa, erro 5xx); se todos falharem, regista `last_error.json`, marca o job como `failed` e segue para o próximo (no mesmo dia se houver cota).
7. **Comando `tools/repair_registry.py`** reconstrói o registry a partir dos DOCX existentes caso o registry seja corrompido.
8. **Comando `tools/rehash.py`** regenera todos os hashes após mudança do motor DOCX.


## 11. ESTRATÉGIA DE VERSIONAMENTO

1. **Versionamento Semântico (SemVer)** no ficheiro `VERSION`: `MAJOR.MINOR.PATCH`
   - MAJOR: mudança incompatível na estrutura do registry / na organização de output.
   - MINOR: novo material_type, nova funcionalidade.
   - PATCH: correcções de bugs, ajuste de prompts.
2. **Versão da apostila** no registry: `versao_sistema` (o SemVer do pipeline que a gerou).
3. **Prompt versioning**: cada template `.j2` tem um hash; o hash é gravado no registry. Alterar um prompt incrementa PATCH.
4. **Curriculum version**: o `curriculum.json` tem `versao_mapa`; o hash do PDF é gravado em `state/.curriculum.sha256`. Alterar o mapa incrementa MINOR.
5. **CHANGELOG automático** em formato Keep a Changelog.
6. **Git tags** em cada marco (M1…M9) e em cada release estável.
7. **Regra de commits** (Conventional Commits alargado):
   ```
   feat(pipeline): adiciona suporte a retry com jitter
   Motivo: …
   Impacto: …
   Ficheiros: src/ebe/ai/backoff.py, src/ebe/ai/gemini_client.py
   Próximos passos: …
   ```
   — nunca mensagens genéricas como “update”.


## 12. ESTRATÉGIA DE MANUTENÇÃO

1. **Workflow de autodiagnóstico semanal** (`autodiagnostic.yml`):
   - Verifica organização do repositório, duplicação de código (com `ruff`), performance (duração média por apostila), saúde da API (teste de ping), segurança (secrets expostos), documentação (módulos sem docstring), qualidade (testes).
   - Escreve relatório em `state/auto_diag/` e actualiza `PROJECT_STATE.md`.
2. **Revisão manual mensal** (pelo utilizador) de uma amostra (5-10) de apostilas do mês para garantir qualidade doutrinária/editorial.
3. **Actualizações de dependências** via Dependabot (futuramente) com PRs pequenas e testadas.
4. **Logs rotativos** (mantêm os últimos 30 dias de corridas).
5. **Documentação viva**: toda alteração a um módulo obriga a actualizar o seu docstring; a doc em `docs/` é actualizada em conjunto com o código.


## 13. SEGURANÇA

- `GEMINI_API_KEY` apenas em GitHub Secrets (`Settings → Secrets and variables → Actions → New repository secret`).
- O `GEMINI_SETUP.md` descreve passo-a-passo (telemóvel) como gerar a chave em Google AI Studio e adicionar ao repo.
- `.gitignore` reforçado: `*.tmp`, `.env`, `state/cache/`, `state/logs/*.log` (estes ficarão apenas como artefactos do workflow e não serão commitados), `__pycache__/`, `.venv/`.
- Nenhum prompt ou logging inclui a chave; uma função `_redact(text)` substitui qualquer sequência de 20+ caracteres alfanuméricos que pareça token.
- Os artefactos .docx são binários; não são executados (sem macros). O python-docx não processa macros, por isso é seguro por desenho.


## 14. ESTRATÉGIA DE TESTES

1. **Testes unitários**: parser, rate limiter, slug, caminhos, validação de currículo, helpers DOCX, calculador de similaridade.
2. **Testes de integração**: pipeline completo contra o mock do Gemini (salva respostas pré-gravadas em `tests/fixtures/`).
3. **Teste de regressão visual**: depois de cada alteração ao motor DOCX, o script gera a apostila piloto e compara o texto + estrutura com a referência.
4. **Teste de carga local**: antes de activar o diário, geração de 3 apostilas seguidas com rate limiting real para medir consumo.


## 15. RESULTADOS ESPERADOS

- 11 apostilas/dia de forma automática.
- Qualidade editorial equivalente à apostila-piloto `EBE-APO-001_Apostila_Piloto_O_Contexto_Imediato.docx`.
- 100% de rastreabilidade (todas as apostilas com registo).
- Zero re-geração de apostila já finalizada.
- Retoma automática após falha.
- Painel `PROJECT_STATE.md` sempre actualizado e legível a partir do telemóvel.
- Após o lote inicial de 1.029, o mesmo pipeline permite gerar livros, e-books, etc., apenas adicionando renderers e prompts.

---

## PRÓXIMOS PASSOS IMEDIATOS (após este plano)

1. Validação do plano por si (utilizador).
2. Criação do `GEMINI_SETUP.md` (guia telemóvel) — só depois de validado.
3. Refatoração do motor DOCX em `src/ebe/docx/` (M1).
4. Construção do cliente Gemini e prompts (M2).
5. Criação dos workflows em `workflows_ready/` (M5).

---

*Documento redigido pela equipa integrada (Arquiteto, Eng. IA, Especialista Gemini, DevOps, Eng. Python, Designer Editorial, Especialista DOCX, Qualidade).*
*Soli Deo Gloria.*
