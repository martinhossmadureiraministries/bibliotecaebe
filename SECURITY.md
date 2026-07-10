# Política de Segurança

## Chave da API Gemini

- A chave da API do Google Gemini (`GEMINI_API_KEY`) **apenas** é armazenada em **GitHub Secrets** (`Settings → Secrets and variables → Actions`).
- **Nunca** a grave em ficheiros, commits, logs, ou issues.
- `.env` e `*.secret` estão em `.gitignore` e **nunca** serão commitados.
- O pipeline possui uma função de redacção (`_redact`) que remove qualquer string que pareça uma chave de API antes de escrever nos logs.
- Se suspeitar que uma chave foi exposta: regenere-a imediatamente no Google AI Studio e actualize o Secret.

## Segredos adicionais

Nenhum segredo adicional está previsto na fase inicial (M0-M5). Caso no futuro existam (tokens de publicação, etc.), seguirão a mesma regra: apenas GitHub Secrets, referências por variável de ambiente, nunca em código.

## Ficheiros gerados

Os ficheiros `.docx` são gerados com `python-docx`, que por desenho não executa macros. Não existe risco de conteúdo executável nos artefatos.

## Relatar vulnerabilidades

Em caso de vulnerabilidade de segurança, contactar a Direcção Pedagógica da EBE em privado. Não crie issues públicas para falhas de segurança antes de estas serem resolvidas.
