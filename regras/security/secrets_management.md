# Gestao de Segredos

## Proibicoes
- NUNCA fazer hardcode de senhas, API keys, tokens ou credenciais no codigo fonte.
- NUNCA commitar arquivos .env, credentials.json, service account keys ou similares.
- NUNCA logar segredos, tokens ou senhas em logs de aplicacao.

## Praticas Obrigatorias
- Usar servicos de gerenciamento de segredos (Secret Manager, Vault, etc.).
- Referenciar segredos via variaveis de ambiente ou montagem de volume seguro.
- Rotacionar credenciais periodicamente (maximo 90 dias para service accounts).
- Arquivos .gitignore devem incluir padroes para arquivos sensiveis (*.key, *.pem, .env*).

## Deteccao
- Strings que parecem tokens (base64 longo, prefixos como "sk-", "ghp_", "AIza") sao suspeitas.
- Conexoes de banco com senha inline (postgres://user:password@host) sao violacoes.
