# OWASP Top 10 — Regras de Seguranca

## A01: Broken Access Control
- Validar autorizacao em TODOS os endpoints (nao apenas autenticacao).
- Nao confiar em dados do cliente para decisoes de autorizacao.
- Implementar principio de menor privilegio.

## A02: Cryptographic Failures
- Usar HTTPS para todas as comunicacoes externas.
- Nao usar algoritmos criptograficos obsoletos (MD5, SHA1 para hashing de senhas).
- Usar bcrypt, scrypt ou Argon2 para hashing de senhas.

## A03: Injection
- Usar queries parametrizadas (prepared statements) — NUNCA concatenar input do usuario em SQL.
- Sanitizar input do usuario antes de usar em comandos de sistema (OS command injection).
- Validar e sanitizar input em templates (Server-Side Template Injection).

## A04: Insecure Design
- Implementar rate limiting em endpoints de autenticacao.
- Validar input no backend (nao confiar apenas em validacao frontend).

## A05: Security Misconfiguration
- Nao expor stack traces ou mensagens de erro detalhadas em producao.
- Desabilitar headers desnecessarios que exponham tecnologia (X-Powered-By).
- Configurar CORS de forma restritiva (nao usar wildcard * em producao).

## A07: Cross-Site Scripting (XSS)
- Escapar output em contextos HTML, JavaScript e URL.
- Usar Content Security Policy (CSP) headers.

## A08: Software and Data Integrity Failures
- Verificar integridade de dependencias (checksums, lock files).
- Nao deserializar dados de fontes nao confiaveis sem validacao.

## A09: Security Logging and Monitoring
- Logar tentativas de autenticacao falhadas.
- Implementar alertas para atividades anomalas.
