# Tratamento de Erros

## Principios
- Nunca silenciar excecoes com `except: pass` ou `except Exception: pass` sem logging.
- Capturar excecoes especificas — evitar `except Exception` generico quando possivel.
- Logar erros com contexto suficiente para diagnostico (stack trace, parametros relevantes).
- Falhar graciosamente — retornar mensagens de erro uteis para o usuario sem expor detalhes internos.

## APIs e Endpoints
- Retornar codigos HTTP apropriados (400 para input invalido, 401/403 para auth, 500 para erros internos).
- Respostas de erro devem ter formato consistente (ex: {"error": "mensagem", "code": "ERROR_CODE"}).
- Nunca retornar stack traces ou mensagens internas em respostas de API de producao.

## Logging
- Usar niveis de log apropriados: ERROR para erros, WARNING para situacoes anomalas, INFO para fluxo normal.
- Incluir correlation ID / request ID em logs para rastreabilidade.
- Nao logar dados sensiveis (senhas, tokens, PII) em mensagens de erro.

## Retry e Resiliencia
- Operacoes de rede devem ter timeout configurado.
- Implementar retry com backoff exponencial para chamadas a servicos externos.
- Definir circuit breaker para dependencias criticas.
