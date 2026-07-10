# MANUAL DE CRIAÇÃO DE NOVOS MAPAS CURRICULARES
> Guia oficial para a criação de mapas de títulos **após as 1.029 apostilas iniciais**
> Versão 1.0 — 2026-07-10 · Escola Bíblica Epignósis

---

## 1. OBJECTIVO

Este manual define o procedimento **padrão, repetível e validado** para criar e publicar **novos mapas curriculares** (conjuntos de títulos de apostilas, cursos, módulos, etc.) que o sistema de geração automática EBE irá processar após concluir o lote inicial das 1.029 apostilas.

Seguindo este manual garante-se:

- **Rastreabilidade** entre mapas (cada mapa tem versão, checksum e data).
- **Consistência** com a Arquitectura Oficial (`EBE-DOC-005`) e o Mapa de Cursos (`EBE-DOC-006`).
- **Imutabilidade** dos títulos do mapa anterior (nunca se renumera ou renomeia apostilas já publicadas).
- **Compatibilidade** com o pipeline automático (GitHub Actions + Gemini).
- **Zero interrupção** da produção diária enquanto se prepara um novo mapa.


## 2. QUANDO CRIAR UM NOVO MAPA

Um novo mapa deverá ser criado sempre que se verifique **uma** das situações:

1. **Conclusão das 1.029 apostilas** do mapa inicial (`EBE-PLAN-APO`).
2. **Criação de novos Institutos, Escolas ou Cursos** não previstos.
3. **Expansão curricular aprovada pela Direcção Pedagógica e pelo Conselho Doutrinário**.
4. **Mudança da sequência ou estrutura de níveis** (decisão de governação).
5. **Criação de novos tipos de material** (livros, avaliações, planos de aula, etc.) que exijam a sua própria lista canónica de títulos — estes usam mapas próprios (ver §8).

NÃO crie um novo mapa para: corrigir um erro de digitação num título, reordenar apostilas dentro de um módulo existente, ou adicionar uma apostila em falta numa lacuna entretanto descoberta. Para isso há o **Procedimento de Correcção de Mapa** (§6).


## 3. CICLO DE VIDA DE UM MAPA

```
┌─────────────────┐
│ RASCUNHO        │  autor trabalha em docs/plan/maps/EBE-PLAN-APO-N-v0rascunho.*
├─────────────────┤
│ REVISÃO         │  revisão pedagógica + doutrinária (pareceres em anexo)
├─────────────────┤
│ APROVAÇÃO       │  Director Geral + Coord. Académica + Cons. Doutrinário
├─────────────────┤
│ PUBLICAÇÃO      │  PDF assinado + curriculum.json gerado + tags
├─────────────────┤
│ ACTIVO          │  pipeline passa a consumir este mapa
├─────────────────┤
│ ENCERRADO       │  todas as apostilas do mapa foram geradas e validadas
└─────────────────┘
```


## 4. ESTRUTURA NUMÉRICA E NOMENCLATURA

### 4.1 Código do mapa
Cada mapa recebe um código institucional:

```
EBE-PLAN-<TIPO>-<VERSÃO>[.<REVISÃO>]
```

- `<TIPO>`: `APO` (apostilas), `LIV` (livros), `AVAL` (avaliações/provas), `PLA` (planos de aula), `APR` (apresentações), `MAN` (manuais), `GUI` (guias de estudo), `EBO` (e-books), `EXE` (exercícios), `INS` (materiais institucionais).
- `<VERSÃO>`: número sequencial inteiro, iniciado em 1. O mapa inicial é `EBE-PLAN-APO-1`.
- `<REVISÃO>` (opcional): `.1`, `.2`, etc., só para correcções que **não** alteram o conjunto de apostilas (ver §6).

Exemplos:
- `EBE-PLAN-APO-1` — 1.029 apostilas iniciais (mapa actual).
- `EBE-PLAN-APO-2` — segundo ciclo de apostilas (expansão).
- `EBE-PLAN-AVAL-1` — mapa de avaliações/provas.
- `EBE-PLAN-LIV-1` — mapa de livros.

### 4.2 Numeração das apostilas

- **As apostilas do novo mapa continuam a sequência numérica global**. Se o mapa 1 termina na apostila **1.029**, o mapa 2 começa na **1.030**.
- Cada apostila recebe código único: `EBE-APO-NNNN` (até 9999; se em algum momento for excedido, passa a `EBE-APO-NNNNN` em nova revisão do sistema).
- **Nunca reutilizar números** de apostilas antigas, mesmo que sejam retiradas. Apostilas retiradas ficam com status `retired` no `registry.jsonl` e não são apagadas.

### 4.3 Nome dos ficheiros

- PDF do mapa: `state/maps/EBE-PLAN-APO-2.pdf`
- JSON canónico: `state/maps/EBE-PLAN-APO-2.json`
- Fontes: `docs/plan/maps/EBE-PLAN-APO-2/` (documentos de trabalho, pareceres, etc.)
- Checksum: `state/maps/EBE-PLAN-APO-2.sha256`


## 5. PROCESSO DE CRIAÇÃO (passo-a-passo)

### Fase A — Preparação
1. **Crie a pasta de trabalho** dentro de `docs/plan/maps/` com o código do novo mapa, ex: `docs/plan/maps/EBE-PLAN-APO-2/`.
2. **Copie o modelo** `docs/plan/templates/mapa_template.md` (será criado na implementação do M3) para a pasta como `PLANO.md` e preencha o cabeçalho:
   - Código do mapa
   - Tipo de material
   - Data de início de redacção
   - Responsáveis (autor, rev. pedagógica, rev. doutrinária)
   - Motivação/justificativa pedagógica
3. **Confirme** que o mapa respeita a Arquitectura Oficial (Nível → Instituto → Escola → Curso → Módulo → Apostila). Novos Institutos/Escolas/Cursos só podem ser criados após actualização de `EBE-DOC-005` e `EBE-DOC-006`.

### Fase B — Redacção da lista de títulos
4. **Defina o número total** de apostilas do novo mapa.
5. **Organize a hierarquia completa**, num documento (Markdown ou DOCX) com esta estrutura (obrigatória):

   ```
   NÍVEL X — <nome>
     Instituto Y — <nome>
       Escola <nome>
         Curso: <nome> · Carga horária: ≈ XX h
           Módulo 1 — <nome>
             1030. <Título>
             1031. <Título>
             ...
           Módulo 2 — <nome>
             ...
   ```

6. **Regras para títulos** (obrigatórias):
   - Cada título é uma **unidade didáctica autocontida** (15-20 páginas).
   - Títulos são **claros, específicos e não se sobrepõem** a outros títulos do mesmo curso ou de cursos anteriores.
   - Evite títulos genéricos como “Introdução a …” sem mais precisão, excepto quando for realmente a primeira apostila introdutória.
   - Evite títulos idênticos a apostilas já existentes (faça uma pesquisa no `state/curriculum.json`).
   - Linguagem académica sóbria, em **pt-PT/pt-AO** (Português europeu/Angola), seguindo o estilo do mapa actual.
   - Nenhum título pode conter caracteres especiais para além de letras, números, espaços, `-`, `,`, `(`, `)`, `«`, `»`, `:`, `?`, `!`. Nada de `/`, `\`, `*`, etc. (que causariam problemas em nomes de ficheiros).

7. **Distribua as apostilas por módulos** de forma coerente (cada módulo deve ter entre 3 e 6 apostilas, idealmente).

### Fase C — Revisão e aprovação
8. **Auto-revisão do autor**: verifique
   - Total de apostilas = somatório por módulo = somatório por curso = total declarado.
   - Numeração contínua, sem saltos nem duplicações.
   - Hierarquia consistente (cada apostila pertence a um módulo, cada módulo a um curso, etc.).
   - Nenhum título coincide com apostilas do mapa anterior.
9. **Revisão pedagógica** pela Coordenação Académica — parecer gravado em `docs/plan/maps/<codigo>/PARECER_PEDAGOGICO.md`.
10. **Revisão doutrinária** pelo Conselho Doutrinário — parecer em `PARECER_DOUTRINARIO.md`.
11. **Aprovação final** pelo Director Geral — assinatura no PDF final.

### Fase D — Publicação (técnica)
12. **Gere o PDF final** com a mesma identidade visual do mapa inicial (capa EBE, paleta `#1B3A5C`/`#2E7D4F`, Garamond), com:
    - Capa
    - Apresentação
    - Quadro-resumo geral
    - Índice
    - Corpo (hierarquia completa)
    - Página final com “Total de apostilas mapeadas: N” e selo Soli Deo Gloria
13. **Coloque o PDF** em `state/maps/EBE-PLAN-<TIPO>-<VER>.pdf`.
14. **Execute o parser**:
    ```bash
    python3 tools/parse_mapa.py --map EBE-PLAN-APO-2 --pdf state/maps/EBE-PLAN-APO-2.pdf --out state/maps/EBE-PLAN-APO-2.json --start-id 1030
    ```
    - O parser valida: total de apostilas, numeração contínua, hierarquia, caracteres proibidos, títulos duplicados com o mapa activo.
15. **Gere o checksum**:
    ```bash
    sha256sum state/maps/EBE-PLAN-APO-2.pdf state/maps/EBE-PLAN-APO-2.json > state/maps/EBE-PLAN-APO-2.sha256
    ```
16. **Actualize `config.yaml`**:
    ```yaml
    curriculum:
      active_map: "EBE-PLAN-APO-2"
      maps:
        - code: "EBE-PLAN-APO-1"
          json: "state/curriculum.json"   # mapa inicial
          status: "closed"                # 1029/1029 concluídas
          last_id: 1029
        - code: "EBE-PLAN-APO-2"
          json: "state/maps/EBE-PLAN-APO-2.json"
          status: "active"
          first_id: 1030
    ```
17. **Adicione a entrada no CHANGELOG** e marque a transição no ROADMAP.
18. **Commit com mensagem padrão** (ver §11).
19. **Crie uma tag Git** `map/EBE-PLAN-APO-2` para marcar o momento da activação.

### Fase E — Entrada em produção
20. Na execução diária seguinte, o scheduler detecta o novo mapa e **começa automaticamente no primeiro ID pendente** (1030, por exemplo).
21. Confirme na primeira execução, pelo `PROJECT_STATE.md`, que o próximo item é a apostila esperada do novo mapa.
22. **Revise manualmente as primeiras 3 apostilas** do novo mapa antes de deixar o ciclo seguir sozinho (são o teste de integração com o novo conteúdo).


## 6. PROCEDIMENTO DE CORRECÇÃO DE MAPA ACTIVO

Se encontrar um erro no mapa **enquanto ele ainda está em produção** (antes de todas as apostilas terem sido geradas):

### 6.1 Erros que NÃO exigem novo mapa (revisão .1, .2, …)
- Gralha num título que **ainda não foi gerado**.
- Troca de ordem entre apostilas **não geradas** dentro do mesmo módulo.
- Correcção do nome de um curso/módulo (apenas se nenhuma apostila sua foi publicada; caso contrário adiciona uma nota histórica no `curriculum.json` em vez de renomear).

**Procedimento**:
1. Edite o fonte do mapa (`docs/plan/maps/.../PLANO.md`).
2. Regenere o PDF com o sufixo de revisão (ex: `EBE-PLAN-APO-2.1.pdf`).
3. Execute o parser com `--allow-reorder-ungenerated`.
4. O parser verificará que nenhuma apostila já gerada foi tocada.
5. Atualize o checksum e o `config.yaml` (adiciona `.1`).
6. Registe a alteração em `docs/plan/maps/.../CHANGELOG_MAPA.md`.

### 6.2 Erros que EXIGEM novo mapa
- Adição/remoção de apostilas depois de já terem sido geradas.
- Reestruturação de níveis/institutos/escolas.
- Alteração do código de contagem global (ex: mudar o tipo de `APO` para outra coisa).

→ Volte ao §5 e crie um novo mapa com a próxima versão.


## 7. CHECKLIST DE VALIDAÇÃO DE UM MAPA (obrigatória antes de activar)

Antes de mudar `active_map`, confirme:

- [ ] O PDF tem capa, apresentação, quadro-resumo, índice e corpo completos.
- [ ] O código do mapa segue a nomenclatura `EBE-PLAN-<TIPO>-<VER>`.
- [ ] O total de apostilas declarado no quadro-resumo é igual ao que o parser extrai.
- [ ] A numeração começa em `last_id + 1` do mapa anterior (sem saltos, sem duplicações).
- [ ] Nenhum título tem caracteres proibidos (`/`, `\`, `*`, etc.).
- [ ] Nenhum título replica integralmente um título do mapa anterior (o parser acusa).
- [ ] Cada apostila está ancorada num `Curso → Módulo` válido.
- [ ] Pareceres pedagógico e doutrinário estão presentes e aprovados.
- [ ] O JSON do mapa valida contra o schema `state/maps/_schema.json`.
- [ ] O checksum SHA-256 foi gerado e guardado.
- [ ] `config.yaml` foi actualizado.
- [ ] Foi criada a tag Git `map/<codigo>`.
- [ ] O CHANGELOG e o ROADMAP foram actualizados.
- [ ] Há plano de revisar as primeiras 3 apostilas depois da activação.


## 8. MAPAS PARA OUTROS TIPOS DE MATERIAL

Os mesmos princípios aplicam-se aos outros materiais previstos:

| Tipo de material | Código TIPO | Ficheiros | Numeração de exemplares |
|------------------|-------------|-----------|-------------------------|
| Apostilas        | `APO`       | `EBE-APO-NNNN` | Sequencial global (1..infinito) |
| Livros           | `LIV`       | `EBE-LIV-NNN`  | Sequencial própria |
| E-books          | `EBO`       | `EBE-EBO-NNN`  | Sequencial própria |
| Manuais          | `MAN`       | `EBE-MAN-<PUB>-NNN` | Por público (ALU/DOC/…), separado |
| Planos de aula   | `PLA`       | `EBE-PLA-NNNN` | Derivados das apostilas (1 plano por apostila) |
| Apresentações    | `APR`       | `EBE-APR-NNNN` | Derivados das apostilas |
| Avaliações/provas| `AVAL`      | `EBE-AVAL-NNNN`| Por curso/módulo |
| Exercícios       | `EXE`       | `EBE-EXE-NNNN` | Podem ser derivados de apostilas |
| Guias de estudo  | `GUI`        | `EBE-GUI-NNN`  | Sequencial própria |
| Materiais institucionais | `INS` | `EBE-DOC-NNN`, `EBE-FRM-NNN`, etc. | Mantêm a numeração já existente |

Cada tipo tem a sua própria pasta `state/maps/`, o seu próprio JSON, o seu próprio renderer e prompt builder (ver `docs/PLANO_ARQUITETURA.md`, §9 — Estratégia de escalabilidade).


## 9. INTEGRAÇÃO COM O PIPELINE AUTOMÁTICO

O pipeline consulta `config.yaml → curriculum.active_map` para saber qual o mapa em produção. Cada entrada no registry guarda também o código do mapa em que a apostila foi criada (`map_code: "EBE-PLAN-APO-1"`), garantindo rastreabilidade.

Ao terminar a última apostila de um mapa (`status=finalized` para todas), o scheduler:
1. Marca o mapa como `closed` em `config.yaml`.
2. **Não começa o próximo mapa automaticamente** — o operador (utilizador) deve activar explicitamente o novo mapa, porque se trata de uma decisão editorial. Entretanto o workflow diário fica em modo “standby”, registando em `PROJECT_STATE.md` que o mapa actual foi concluído e aguardando a publicação do próximo.


## 10. EXEMPLO COMPLETO — MAPA 2 (cenário fictício)

**Cenário:** Concluídas as 1.029 apostilas do `EBE-PLAN-APO-1`, a Direcção aprova um novo mapa `EBE-PLAN-APO-2` com mais 150 apostilas de "Escola de Aconselhamento Pastoral Avançado" e "Escola de Missões Transculturais Avançado".

1. Pasta criada: `docs/plan/maps/EBE-PLAN-APO-2/`.
2. Títulos redigidos: 150 apostilas numeradas de 1030 a 1179.
3. PDF gerado: `state/maps/EBE-PLAN-APO-2.pdf` (17 páginas).
4. Execução:
   ```bash
   python3 tools/parse_mapa.py --map EBE-PLAN-APO-2 \
       --pdf state/maps/EBE-PLAN-APO-2.pdf \
       --out state/maps/EBE-PLAN-APO-2.json \
       --start-id 1030
   # → "Total extraído: 150 / esperado 150; faltantes 0; duplicados 0"
   ```
5. Checksum SHA-256 gerado.
6. `config.yaml` actualizado (active_map = "EBE-PLAN-APO-2").
7. Tag `map/EBE-PLAN-APO-2` criada e pushada.
8. No workflow diário seguinte, o pipeline gera a apostila 1030.
9. As apostilas 1030, 1031 e 1032 são revistas manualmente pela Direcção antes de prosseguir.


## 11. MODELO DE COMMIT DE PUBLICAÇÃO DE MAPA

```
feat(curriculum): publica mapa EBE-PLAN-APO-2 com 150 novas apostilas

Motivo: Conclusão das 1.029 apostilas iniciais e aprovação da expansão
curricular pela Direcção Pedagógica e Conselho Doutrinário (pareceres
em docs/plan/maps/EBE-PLAN-APO-2/).

Impacto: O pipeline passará a gerar apostilas de 1030 a 1179 a partir
da próxima execução diária. O mapa anterior (EBE-PLAN-APO-1) é marcado
como closed mas o seu registo permanece imutável.

Ficheiros:
  - state/maps/EBE-PLAN-APO-2.pdf
  - state/maps/EBE-PLAN-APO-2.json
  - state/maps/EBE-PLAN-APO-2.sha256
  - docs/plan/maps/EBE-PLAN-APO-2/* (pareceres, PLANO.md)
  - config.yaml
  - CHANGELOG.md
  - ROADMAP.md

Próximos passos:
  1. Acompanhar geração das apostilas 1030, 1031, 1032.
  2. Validar qualidade editorial e doutrinária.
  3. Se tudo correcto, deixar o ciclo diário prosseguir automaticamente.
```


## 12. DIRECTÓRIOS (serão criados automaticamente na fase M3)

```
docs/plan/
  templates/
    mapa_template.md        # Modelo de ficha de plano de mapa
  maps/
    EBE-PLAN-APO-2/
      PLANO.md              # Plano em si
      PARECER_PEDAGOGICO.md
      PARECER_DOUTRINARIO.md
      CHANGELOG_MAPA.md
    ...
state/
  maps/
    _schema.json            # JSON Schema para validar mapas
    EBE-PLAN-APO-1.pdf      # mapa inicial (cópia)
    EBE-PLAN-APO-1.sha256
    EBE-PLAN-APO-2.pdf
    EBE-PLAN-APO-2.json
    EBE-PLAN-APO-2.sha256
```

> O mapa inicial (`EBE-PLAN-APO-1`) corresponde ao `state/curriculum.json` já criado a partir de `EBE_Mapa_Completo_Apostilas-2.pdf`. O sistema fará a retro-migração para o formato padrão na fase M3 (sem alterar IDs nem títulos).


## 13. REGRAS DE OURO

1. **Nunca** renumerar apostilas já publicadas.
2. **Nunca** alterar um título de apostila já finalizada sem uma apostila de errata explícita (ou uma nova revisão da apostila com versão `.2`).
3. **Nunca** criar novas apostilas sem pareceres favoráveis do pedagógico e do doutrinário.
4. **Nunca** fazer push de um mapa novo sem ter gerado e validado o JSON e o checksum.
5. **Sempre** que um mapa for encerrado, registar a data de conclusão no `CHANGELOG.md`.
6. **Sempre** manter uma cópia PDF assinada de cada mapa (é o documento institucional legal).
7. **Sempre** usar a mesma identidade visual (Garamond, paleta EBE, selo Soli Deo Gloria).
8. **Sempre** escrever em pt-PT/pt-AO, versão ARC quando citar Escrituras.
9. **Sempre** que um novo Instituto/Escola/Curso for criado, actualizar antes `EBE-DOC-005` e `EBE-DOC-006`.
10. **Nunca** apagar ficheiros de mapas antigos — eles fazem parte do arquivo histórico da escola.

---

*Soli Deo Gloria.*
