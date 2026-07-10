# PROJECT STATE · Sistema de Geração de Apostilas EBE
> Actualizado automaticamente pelo pipeline. **Não editar manualmente** entre os marcadores `<!-- AUTO:STATE:BEGIN -->` e `<!-- AUTO:STATE:END -->`.

<!-- AUTO:STATE:BEGIN -->
<!-- AUTO:STATE:END -->

---

## Marcos (resumo manual)

- ✅ **M0** — Plano de arquitectura e base documental
- ✅ **M1** — Refactoring do motor DOCX (`src/ebe/docx/`)
- ✅ **M2** — Esqueleto do cliente Gemini + prompts + rate-limiter (com modo simulate)
- ✅ **M3** — Core do pipeline, curriculum repository, registry, retomada por checkpoint
- ✅ **M4** — Verificador de originalidade (embeddings + similaridade cosseno)
- ✅ **M5** — Workflows GitHub Actions em `workflows_ready/`
- ✅ **M6** — Observabilidade (PROJECT_STATE auto, CHANGELOG, ROADMAP)
- ⏳ **M7** — Primeiro lote de 11 apostilas reais, com chave API do utilizador
- ⏳ **M8** — Produção contínua 11/dia
- ⏳ **M9** — Extensão a outros formatos (livros, avaliações, etc.)

## Saúde do repositório (diagnóstico inicial)

- Estrutura de pacote `src/ebe/`: ✅
- `state/curriculum.json` válido (1029/1029): ✅
- Motor DOCX modular (`src/ebe/docx/`): ✅
- Pipeline ponta-a-ponta testado em modo simulate: ✅
- Workflows em `workflows_ready/`: ✅
- Guia Gemini passo-a-passo (telemóvel): ✅
- `GEMINI_API_KEY`: ⏳ por configurar (ver `docs/GEMINI_SETUP.md`)

## Como arrancar

1. Siga `docs/GEMINI_SETUP.md` para criar a chave Gemini gratuita e adicionar como Secret.
2. Mova os ficheiros de `workflows_ready/` para `.github/workflows/` (instruções no guia).
3. Accione manualmente o workflow `EBE — Geração Diária de Apostilas` com `count=1`.
4. Passe a acompanhar o progresso em `PROJECT_STATE.md`.
