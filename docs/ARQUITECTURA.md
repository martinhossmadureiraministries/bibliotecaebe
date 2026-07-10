# 🏗️ Arquitectura do Sistema EBE

## Visão Geral

O sistema é composto por **5 camadas** que trabalham de forma integrada:

```
┌─────────────────────────────────────────┐
│        CLI / GitHub Actions             │ User Interface
├─────────────────────────────────────────┤
│         Core Pipeline                   │ Orquestração
│  (generate, resume, validate)           │
├─────────────────────────────────────────┤
│  AI (Gemini) │ Curriculum │ Registry    │ Data & Logic
├─────────────────────────────────────────┤
│  DOCX Builder │ Embedding │ Storage     │ Execution
├─────────────────────────────────────────┤
│   GitHub API │ File System │ Logs       │ Infrastructure
└─────────────────────────────────────────┘
```

## Camadas

### 1. **Interface (CLI / Workflows)**
- `src/ebe/cli.py` — Interface de linha de comando
- `.github/workflows/*.yml` — Execução automática (schedule, manual, webhooks)

### 2. **Pipeline Core**
- `src/ebe/core/pipeline.py` — Orquestração principal
- `src/ebe/core/scheduler.py` — Agendamento de tarefas
- `src/ebe/core/resume.py` — Recuperação de falhas (checkpoints)

### 3. **Lógica de Negócio**
- `src/ebe/ai/gemini_client.py` — Integração API
- `src/ebe/curriculum/` — Modelos e validação
- `src/ebe/registry/manager.py` — Controlo de geração

### 4. **Execução**
- `src/ebe/docx/builder.py` — Construtor de documentos
- `src/ebe/ai/originality.py` — Verificação por embeddings
- `src/ebe/utils/` — Utilitários diversos

### 5. **Infraestrutura**
- GitHub API (commits, issues, releases)
- File system (state/, output/, docs/)
- JSON Logs estruturados

## Fluxo de Dados

### Geração de uma Apostila (simplificado)

```
1. CLI: ebe generate --count 1
   ↓
2. Pipeline.generate(count=1)
   ↓
3. Curriculum.next_pending() → Apostila#001
   ↓
4. GeminiClient.generate_content(outline, system_instruction)
   ↓
5. Originality.check_similarity(content) → similaridade < 0.75?
   │ ├─ SIM: Regenerar (max 3 tentativas)
   │ └─ NÃO: Aprovar
   ↓
6. DocumentBuilder.render(content) → apostila.docx
   ↓
7. Registry.add(apostila_id, hash, metadata)
   ↓
8. Commit para GitHub (output/apostilas/)
   ↓
9. PROJECT_STATE.md actualizada (auto)
```

## Modelos de Dados

### Apostila (Curriculum Item)

```json
{
  "id": "APO-001-2026",
  "codigo_ebe": "EBE-APO-001",
  "instituto": "Instituto de Ciências Teológicas",
  "escola": "Escola de Hermenêutica",
  "curso": "Introdução à Hermenêutica",
  "modulo": 3,
  "nivel": "Crescimento",
  "titulo": "O Contexto Imediato",
  "carga_horaria": 3,
  "versao": "0.1.0",
  "status": "pending" | "in_progress" | "completed" | "rejected",
  "data_criacao": "2026-07-10T12:00:00Z",
  "autores_ia": ["gemini-1.5-pro"],
  "hash_conteudo": "abc123...",
  "similaridade": 0.42,
  "tentativas_regeneracao": 0
}
```

### Registry Entry

```json
{
  "apostila_id": "APO-001-2026",
  "timestamp": "2026-07-10T13:05:00Z",
  "status": "completed",
  "arquivo_saida": "output/apostilas/APO-001_O_Contexto_Imediato.docx",
  "hash_conteudo": "abc123...",
  "paginas": 18,
  "tempo_geracao_ms": 45000,
  "custo_tokens": {"entrada": 12500, "saida": 8300},
  "validacoes": {
    "qualidade_conteudo": "PASS",
    "formato_docx": "PASS",
    "referencias_biblicas": "PASS",
    "originalidade": "PASS"
  }
}
```

## Padrões de Design

### 1. Builder Pattern

```python
# Construir documento passo-a-passo
builder = DocumentBuilder("titulo", "codigo")
builder.add_capa()
builder.add_marco_filosofico()
builder.add_secoes(conteudo)
builder.add_exercicios(exercicios)
doc = builder.build()  # → Document
```

### 2. Repository Pattern

```python
# Acesso abstrato aos dados
curriculum = CurriculumRepository()
apositlas = curriculum.find_pending(limit=10)
for apo in apostilas:
    curriculum.mark_in_progress(apo.id)
```

### 3. Factory Pattern

```python
# Criar clientes conforme configuração
client = DocumentClientFactory.create(
    tipo="docx",
    formato="apostila"
)
```

### 4. Observer Pattern

```python
# Notificar múltiplos listeners de eventos
pipeline.on("apostila_generated", lambda e: log(e))
pipeline.on("apostila_generated", lambda e: commit_github(e))
pipeline.on("apostila_generated", lambda e: update_state(e))
```

## Estado da Aplicação

### Ficheiro de Estado: `state/curriculum.json`

Armazena mapa completo das 1.029 apostilas com status:

```json
{
  "meta": {
    "total_apostilas": 1029,
    "total_completas": 45,
    "total_pendentes": 984,
    "ultima_actualizacao": "2026-07-10T15:00:00Z"
  },
  "apostilas": [
    { "id": "APO-001", "status": "completed", ... },
    { "id": "APO-002", "status": "pending", ... },
    ...
  ]
}
```

### Ficheiro de Registo: `state/registry.jsonl`

Log estruturado (newline-delimited JSON) de cada geração:

```
{"apostila_id":"APO-001","timestamp":"...","status":"completed",...}
{"apostila_id":"APO-002","timestamp":"...","status":"completed",...}
...
```

## Tratamento de Erros

### Camadas de Recuperação

1. **Rate Limiting** — `tenacity.wait_exponential()`
2. **Checkpoint** — Salva progresso antes de cada geração
3. **Retry com Backoff** — Max 3 tentativas por apostila
4. **Fall-through Logging** — Log em `state/last_error.json`
5. **Manual Recovery** — CLI: `ebe resume` retoma do checkpoint

### Exceções Customizadas

```python
EBEError (base)
├── ConfigError — Falta chave API, etc.
├── CurriculumError — Validação de currículo
├── DocumentError — Erro na geração DOCX
├── OriginalityError — Falha verificação
├── GeminiError — Erro API
└── RateLimitError — Quota esgotada
```

## Segurança

### Acessos

- **Leitura:** Qualquer utilizador (public repo)
- **Escrita:** GitHub Actions (GITHUB_TOKEN)
- **Geração IA:** Apenas com GEMINI_API_KEY (GitHub Secret)

### Validação

- Entrada: Pydantic models com type hints
- Referências bíblicas: Regex contra lista conhecida
- Conteúdo IA: Verificação de "hallucinations" (M4)

## Performance

### Targets

- **Geração por apostila:** ~45-60 segundos (M2 em cloud, M1 em dev sim)
- **Throughput:** 11 apostilas/dia (cota gratuita Gemini)
- **Similaridade check:** <5 segundos (embeddings cached)
- **Commit:** <2 segundos por apostila (batching)

### Optimizações

1. **Caching de embeddings** — Evita recompute
2. **Batch commits** — 11 apostilas = 1 commit
3. **Lazy loading** — Curriculum carrega à demanda
4. **Async I/O** — Leitura paralela de ficheiros (M2+)

---

**Próximo Marco:** M2 — Implementação do Cliente Gemini + Rate Limiter
