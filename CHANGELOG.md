# CHANGELOG · Sistema de Geração de Apostilas EBE
> Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) · Versão SemVer.

<!-- AUTO:CHANGELOG:BEGIN -->

## [0.1.0] — 2026-07-10 — Marco M0 · Plano e Fundação

### Adicionado
- **Documento fundador do repositório**: `docs/PLANO_ARQUITETURA.md` com a arquitectura completa do sistema: visão, camadas, estrutura de pastas, módulos, fluxo ponta-a-ponta, tecnologias, cronograma (M0–M9), riscos, estratégias de escalabilidade, recuperação, versionamento e manutenção.
- **Manual de Criação de Novos Mapas** (`docs/MANUAL_CRIACAO_MAPAS.md`): procedimento para publicar mapas curriculares após as 1.029 iniciais, incluindo nomenclatura, ciclo de vida, revisão pedagógica/doutrinária, publicação, correcções e integração com o pipeline.
- **Parser do PDF do mapa curricular** (`tools/parse_mapa.py`): extrai automaticamente a hierarquia Nível → Instituto → Escola → Curso → Módulo → Apostila a partir de `EBE_Mapa_Completo_Apostilas-2.pdf`.
- **Fonte de verdade canónica** (`state/curriculum.json`): 1.029 apostilas extraídas com sucesso, zero faltantes, zero duplicadas, com IDs, títulos, caminho curricular e carga horária.
- **Painel de estado** (`PROJECT_STATE.md`): primeiro preenchimento automático com progresso 0/1029, próximos passos e saúde do repositório.
- **Estrutura base de pastas**: `src/ebe/`, `docs/`, `assets/`, `state/` (logs, hashes, embeddings, cache), `output/`, `tools/`, `workflows_ready/`.
- **Recursos estáticos**: cópia dos logotipos para `assets/` (logo_ebe, logo_pequeno, logo_emblema, logo_marca_dagua), mantendo retrocompatibilidade com `_assets/`.
- **Este CHANGELOG** (automático por blocos delimitados) e **ROADMAP** inicial.

### Confirmado
- Total de apostilas no mapa: **1.029** (1029/1029 após parsing).
- IDs de 1 a 1029 cobrem todos os 4 níveis, 10 institutos, 54 escolas, 146 cursos e 343 módulos conforme o quadro-resumo oficial do PDF.

### Decisões técnicas
- Python 3.11+ como runtime; `python-docx` + `google-generativeai` + `jinja2` como stack principal.
- Modelo Gemini padrão: `gemini-2.0-flash` (gratuito) com `text-embedding-004` para controlo de similaridade e `CachedContent` para system instruction.
- Persistência inicial em JSON/JSONL com padrão Repository para permitir migração futura para SQLite/PostgreSQL.
- Rate-limit conservador inicial (5 RPM / 500k TPM / 1000 RPD) para evitar bloqueios na conta gratuita, ajustável por `config.yaml`.
- Nomenclatura de ficheiros e códigos institucionais mantida (ex: `EBE-APO-NNNN`).

### Estratégia de branches
- Devido à regra de sessão do Arena, o trabalho decorre em `arena/019f4b1b-bibliotecaebe`; no final de cada marco validado será orientado o merge para `main` (sem PRs internos desnecessários, conforme solicitado).

<!-- AUTO:CHANGELOG:END -->
