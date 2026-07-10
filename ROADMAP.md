# ROADMAP · Sistema de Geração de Apostilas EBE
> Actualizado automaticamente pelo pipeline. Manter este ficheiro em sintonia com o plano.

<!-- AUTO:ROADMAP:BEGIN -->

## ✅ Concluído (Marco M0)

- [x] Reconhecimento do repositório existente (código e documentos herdados).
- [x] Leitura integral do PDF do mapa (`EBE_Mapa_Completo_Apostilas-2.pdf`).
- [x] Implementação do parser e geração de `state/curriculum.json` (1.029/1.029, sem falhas).
- [x] Plano de Arquitetura completo (`docs/PLANO_ARQUITETURA.md`).
- [x] Manual de Criação de Novos Mapas (`docs/MANUAL_CRIACAO_MAPAS.md`).
- [x] Estrutura base de pastas (`src/ebe/`, `state/`, `output/`, `tools/`, `docs/`, `assets/`, `workflows_ready/`).
- [x] `PROJECT_STATE.md`, `CHANGELOG.md`, este `ROADMAP.md`.
- [x] Decisão de stack e dependências (a registar em `requirements.txt` e `pyproject.toml` no M1).

## 🟡 Em andamento (sessão actual)

- [ ] Aprovação do plano (aguarda validação do utilizador).
- [ ] Criação do guia `docs/GEMINI_SETUP.md` com instruções passo-a-passo (telemóvel) para criar chave API e configurar GitHub Secret — será criado antes do M2.
- [ ] Preparação do esqueleto de pacote `src/ebe/` (__init__, __main__, config, logging, exceptions).

## ⏳ Próximos passos (por ordem)

### M1 — Refactoring do motor DOCX
- [ ] Migrar `_estilos.py` para `src/ebe/docx/styles.py` com API estável.
- [ ] Criar componentes modulares por secção (`sections/capa.py`, `capitulo.py`, etc.).
- [ ] Montar um `DocumentBuilder` que produz apostilas no padrão editorial.
- [ ] Gerar novamente a apostila piloto (EBE-APO-001) pelo novo motor e comparar com a referência visual.

### M2 — Cliente Gemini + prompts
- [ ] `ai/gemini_client.py` com wrapper seguro e `CachedContent`.
- [ ] `ai/rate_limiter.py` (token bucket) e `ai/backoff.py` (tenacity).
- [ ] Templates Jinja2 para system_instruction, outline, secções, exercícios, glossário.
- [ ] `docs/GEMINI_SETUP.md` com instruções detalhadas para telemóvel (como criar chave, adicionar ao Secret, testar, validar, resolver erros).
- [ ] Teste local: gerar uma apostila de amostra com uma chave de teste.

### M3 — Core do pipeline
- [ ] `curriculum/` (models + repository + validator).
- [ ] `core/pipeline.py`, `core/scheduler.py`, `core/resume.py`.
- [ ] `registry/` (manager + hash) com `state/registry.jsonl`.
- [ ] Retro-migração do mapa inicial para o formato padrão `state/maps/EBE-PLAN-APO-1.*` sem quebrar IDs.
- [ ] Escrita atómica e checkpoints.
- [ ] Teste: geração ponta-a-ponta de 3 apostilas locais.

### M4 — Originalidade
- [ ] `ai/originality.py` com embeddings (`text-embedding-004`) e comparação por cosseno.
- [ ] Regeneração automática quando o limiar for excedido (máx. 3 tentativas).
- [ ] Validação de referências bíblicas (`utils/bible_refs.py`).
- [ ] Medição de páginas após render com ciclo de feedback à IA para atingir 15-20 páginas sem artifícios.

### M5 — Workflows GitHub Actions
- [ ] `workflows_ready/daily_generate.yml` (schedule 04:00 UTC, 11 apostilas/dia).
- [ ] `workflows_ready/validate.yml` (validação de estrutura e qualidade).
- [ ] `workflows_ready/update_dashboard.yml` (actualiza PROJECT_STATE / CHANGELOG / ROADMAP).
- [ ] `workflows_ready/autodiagnostic.yml` (revisão semanal).
- [ ] Instruções no `GEMINI_SETUP.md` sobre como mover para `.github/workflows/` a partir do telemóvel.
- [ ] Primeira execução automática em GitHub.

### M6 — Observabilidade
- [ ] `state/` com logs estruturados, `last_error.json`, relatórios.
- [ ] Actualização automática de PROJECT_STATE/CHANGELOG/ROADMAP.
- [ ] Autodiagnóstico semanal: organização, duplicação, desempenho, segurança, dívida técnica.

### M7 — Primeiro lote
- [ ] Primeiras 11 apostilas em produção.
- [ ] Revisão editorial manual das primeiras 3.
- [ ] Ajustes finos de prompts e estilos com base na revisão.

### M8 — Produção contínua
- [ ] 11 apostilas/dia até concluir as 1.029.
- [ ] Monitorização diária (via PROJECT_STATE.md acessível do telemóvel).
- [ ] Revisão manual amostral mensal (5-10 apostilas).

### M9 — Extensão a outros formatos
- [ ] Sistema de plugins de material_type.
- [ ] Mapas próprios para LIV, EBO, MAN, PLA, APR, AVAL, EXE, GUI, INS.
- [ ] Novos renderers (e.g., PDF, HTML para e-book) e prompts específicos.

## 💡 Melhorias futuras (backlog)

- Integração com Google Drive/OneDrive para distribuição automática.
- Interface web administrativa (Streamlit/FastAPI) para acompanhamento do progresso.
- Aprovação/rejeição de apostilas via comentários no GitHub.
- Rotação de múltiplas chaves Gemini para maior cota.
- Migração opcional para PostgreSQL caso o volume justifique.
- Geração automática de certificados associados a cada apostila/módulo/curso.
- Revisão gramatical automatizada em pt-PT (ferramenta) antes da publicação.
- Módulo de detecção de hallucinations (afirmações teológicas sensíveis) com base na Declaração de Fé.

## ⚠️ Riscos conhecidos a mitigar em próximos marcos

- Atrasos por esgotamento de cota gratuita → mitigado em M2 com rate-limit e medição.
- Qualidade/originalidade insuficiente nas primeiras apostilas → mitigado em M4 + revisão manual das primeiras.
- Dificuldade de operação por telemóvel → mitigado com `GEMINI_SETUP.md` detalhado e PROJECT_STATE.md simples de ler.
- Branches em conflito com a orientação inicial (main vs arena) → notas no CHANGELOG e orientação de merge.

<!-- AUTO:ROADMAP:END -->
