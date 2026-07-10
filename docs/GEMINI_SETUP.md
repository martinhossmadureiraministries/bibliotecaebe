# GUIA DE CONFIGURAÇÃO DA API GEMINI (ANDROID/TELEMÓVEL)
> Guia passo-a-passo (ecrã-a-ecrã) para criar a sua chave **gratuita** da API Google Gemini, configurá-la no repositório GitHub como Secret, testar e validar o funcionamento — tudo a partir do telemóvel, sem precisar de computador.

A API do Gemini é **gratuita** para os limites que o nosso sistema utiliza (até 15 pedidos por minuto; cerca de 1 milhão de tokens por minuto; 1.500 pedidos por dia com o modelo Flash). O nosso sistema tem rate-limiting conservador e **nunca** consome mais do que isso.

---

## 0. PRÉ-REQUISITOS (no telemóvel)
- Ter uma Conta Google (pode ser a mesma que usa para o Gmail).
- Ter o navegador do telemóvel (Chrome recomendado).
- Ter sessão iniciada no GitHub e acesso de escrita/edição ao repositório `martinhossmadureiraministries/bibliotecaebe`.

---

## PASSO 1 — CRIAR A CHAVE DA API GEMINI (3 minutos)

1. **Abra o navegador** do telemóvel e vá para:
   👉 **https://aistudio.google.com/apikey**
2. Se for pedido, **inicia sessão com a sua conta Google**.
3. No ecrã "API keys", toque no botão azul **"Create API key"** (Criar chave API).
   - Se aparecer um diálogo "Select a Google AI Studio project", escolha **"Create new project"** (criar novo projecto) ou seleccione um existente. O nome não importa.
4. Será gerada uma chave semelhante a:
   ```
   AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
   (cerca de **39 caracteres**, começada por `AIza`).
5. **Toque em "Copy"** (copiar) para copiar a chave para a área de transferência do telemóvel.
6. **Cole a chave num bloco de notas temporário** (apenas para não a perder enquanto navega).
   - ⚠️ NÃO envie a chave por WhatsApp, e-mail público, redes sociais, nem a escreva em comentários, issues, ou commits do GitHub.

> 💡 Se em qualquer altura suspeitar que a chave foi exposta, volte a `aistudio.google.com/apikey`, apague a chave antiga com o ícone de 🗑️ (caixote do lixo) e crie uma nova. O pipeline aceitará a nova chave assim que actualizar o Secret no Passo 2.

---

## PASSO 2 — ADICIONAR A CHAVE COMO SECRET NO GITHUB (2 minutos)

A chave NUNCA deve ser gravada no código. Vamos guardá-la como **GitHub Secret** (o GitHub Actions pode ler o valor, mas ninguém o vê novamente, nem você).

1. Abra o navegador e vá ao repositório:
   👉 **https://github.com/martinhossmadureiraministries/bibliotecaebe**
2. Na barra de navegação do repositório, toque em **"Settings"** (Definições).
   - 📱 Se o botão Settings não estiver visível no telemóvel, deslize a barra ou toque em "…" (More).
3. No menu lateral esquerdo, desça até **"Secrets and variables"** → toque em **"Actions"**.
4. Toque no botão verde **"New repository secret"** (Novo segredo do repositório).
5. No campo **"Name"** (Nome) escreva EXACTAMENTE (tudo em maiúsculas, sublinhado):
   ```
   GEMINI_API_KEY
   ```
6. No campo **"Secret"**, **cole a chave** que copiou no Passo 1 (a que começa por `AIza…`).
7. Toque no botão verde **"Add secret"**.

✅ Feito! A chave está guardada em segurança. Daqui em diante **não precisa de a voltar a ver** — o pipeline usa-a automaticamente.

---

## PASSO 3 — COLOCAR OS WORKFLOWS NA PASTA `.github/workflows/`

Os ficheiros de automação estão em `workflows_ready/` (preparados por nós). Agora que já está no repositório, é necessário movê-los para a pasta onde o GitHub os detecta. Faça isto **uma única vez**, no navegador do telemóvel:

1. No repositório (GitHub web), toque na pasta **`workflows_ready/`**.
2. Abra o ficheiro **`daily_generate.yml`**.
3. Toque no ícone de lápis ✏️ ("Edit this file") no canto superior direito.
4. No campo superior do editor, onde diz **"Name"** (nome do ficheiro, acima do conteúdo), altere o caminho de:
   ```
   workflows_ready/daily_generate.yml
   ```
   para:
   ```
   .github/workflows/daily_generate.yml
   ```
   (pode ter que escrever o novo caminho inteiro).
5. No fim da página, toque em **"Commit changes"** (guardar alterações), escreva uma breve nota como `activar workflow diário` e toque novamente em "Commit changes".
6. Repita os passos 2 a 5 para os outros 3 ficheiros:
   - `workflows_ready/validate.yml` → `.github/workflows/validate.yml`
   - `workflows_ready/autodiagnostic.yml` → `.github/workflows/autodiagnostic.yml`
   - `workflows_ready/update_dashboard.yml` → `.github/workflows/update_dashboard.yml`

> 💡 Dica: se tiver dificuldade em mover pelo telemóvel, pode igualmente apagar os ficheiros de `workflows_ready/` depois de os copiar para `.github/workflows/`, mas não é obrigatório.

---

## PASSO 4 — TESTAR A API E VALIDAR FUNCIONAMENTO

Depois de mover pelo menos o `daily_generate.yml` e adicionar o Secret:

1. No GitHub web, toque no separador **"Actions"** do repositório.
2. Na lista da esquerda, escolha **"EBE — Geração Diária de Apostilas"**.
3. Toque no botão **"Run workflow"** (Executar workflow), à direita, por cima da lista.
4. Mantenha os valores pré-definidos:
   - **Count**: deixe em `1` (gera apenas uma apostila, para teste).
   - **Simulate**: **não** marque (deixe desmarcado, para gerar a apostila real).
5. Toque no botão verde **"Run workflow"**.
6. Aguarde — irá aparecer uma nova linha na lista (em amarelo, "running").
7. Toque nessa linha → depois toque em **"generate"** (a job) para ver os logs ao vivo.
8. Quando vir uma linha como:
   ```
   ✓ Apostila #0001 guardada em output/N01/...
   ```
   — o teste passou! 🎉

---

## PASSO 5 — INTERPRETAR RESULTADOS E ERROS

### ✅ Quando tudo corre bem
- A execução termina com ✅ (verde) na lista de Actions.
- No final do log aparece "Pipeline concluído".
- O painel `PROJECT_STATE.md` é automaticamente actualizado com o progresso.
- É feito um commit automático na branch com o(s) novo(s) DOCX em `output/...`.

### ⚠️ Erros comuns e como resolvê-los

#### Erro 1: "GEMINI_API_KEY não está definida" / "API key not valid"
**Causa:** o Secret não foi criado, ou o nome não está exactamente `GEMINI_API_KEY`.
**Resolver:** volte ao Passo 2; confirme que o nome do Secret é `GEMINI_API_KEY` (maiúsculas, sublinhado). Se a chave for antiga, apague-a e gere uma nova em aistudio.google.com/apikey.

#### Erro 2: "429 Resource Exhausted" / "Quota exceeded" / "Rate limit"
**Causa:** esgotou o limite de pedidos da cota gratuita num dia/minuto.
**Resolver:** o nosso sistema tem **retries automáticos** com backoff. O workflow aguarda e tenta novamente. Se o limite diário (1.500 RPD) for atingido, o workflow pára e retoma no dia seguinte (existe checkpoint para não recomeçar do zero). Não precisa de fazer nada.

#### Erro 3: O workflow pára em "pip install"
**Causa rara:** falha de rede no runner do GitHub.
**Resolver:** basta re-executar: no ecrã da run, toque em **"Re-run jobs"** (botão 🔄 no canto superior direito).

#### Erro 4: "Resposta não é JSON válido"
**Causa rara:** o Gemini por vezes devolve texto que não é JSON puro.
**Resolver:** o sistema tenta novamente automaticamente (até 3 vezes). Se continuar, será registado como falha na apostila; o próximo ciclo diário tentará de novo.

#### Erro 5: Permission denied ao fazer push
**Causa:** as permissões do GITHUB_TOKEN estão restritas.
**Resolver:**
1. Vá a **Settings** → **Actions** → **General** (no fundo do menu).
2. Desça até **"Workflow permissions"**.
3. Marque **"Read and write permissions"**.
4. Guarde (Save).
5. Re-execute o workflow.

---

## PASSO 6 — CONFIRMAR O ESTADO DIARIAMENTE SEM ENTRAR EM ACTIONS

Depois de cada execução, abra o ficheiro **`PROJECT_STATE.md`** no GitHub (na página inicial do repositório, ele estará listado). No topo verá:
- Quantas apostilas foram criadas;
- Quantas faltam;
- Qual foi a última apostila;
- Qual é a próxima;
- Estado da API;
- Último erro (se algum);
- Barra de progresso.

Tudo é actualizado automaticamente — basta abrir o ficheiro no telemóvel para ver como vai.

---

## PASSO 7 — PRODUÇÃO CONTÍNUA (11 apostilas/dia)

Depois de um teste bem-sucedido com 1 apostila, deixe o schedule trabalhar: todos os dias, às **05:00 de Luanda** (04:00 UTC), o workflow corre e gera **11 apostilas novas**, faz commit e actualiza o estado. Você só precisa de:

1. De vez em quando, abrir `PROJECT_STATE.md` para confirmar.
2. Uma vez por mês, abrir 2 ou 3 apostilas ao acaso para revisão manual.
3. Se vir algum erro (aparecerá no PROJECT_STATE e no log do Actions), resolver como descrito no Passo 5.

A produção completa das 1.029 apostilas, a 11/dia, demorará **aproximadamente 94 dias** (cerca de 3 meses e meio).

---

## SEGURANÇA — REGRAS DE OURO

1. ❌ **NUNCA** escreva a chave em ficheiros de código.
2. ❌ **NUNCA** tire capturas de ecrã mostrando a chave.
3. ❌ **NUNCA** envie a chave por WhatsApp/Telegram/SMS/e-mail a pessoas não autorizadas.
4. ❌ **NUNCA** faça commit de um ficheiro `.env` com a chave (o `.gitignore` já bloqueia isso).
5. ✅ Se suspeitar de exposição, gere uma chave nova e substitua o Secret no GitHub.

---

## PROBLEMAS QUE NÃO CONSEGUE RESOLVER?

No próprio repositório:
- Verifique o ficheiro `PROJECT_STATE.md` (painel de estado).
- Verifique o último erro em `state/last_error.json` (se existir).
- Abra o último log em `state/logs/` (se estiver visível).
- Toque em Actions → escolha a run → desça até encontrar a linha vermelha com o erro.

Tire uma captura de ecrã dessa linha e envie ao responsável técnico. Não há necessidade de mexer em código a partir do telemóvel.

---

*Guia preparado para ser lido em ecrã pequeno. Soli Deo Gloria.*
