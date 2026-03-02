# Secrets Management

## Prohibitions
- NEVER hardcode passwords, API keys, tokens, or credentials in source code.
- NEVER commit .env files, credentials.json, service account keys, or similar files.
- NEVER log secrets, tokens, or passwords in application logs.

## Required Practices
- Use secrets management services (Secret Manager, Vault, etc.).
- Reference secrets via environment variables or secure volume mounts.
- Rotate credentials periodically (maximum 90 days for service accounts).
- .gitignore files must include patterns for sensitive files (*.key, *.pem, .env*).

## Detection
- Strings that look like tokens (long base64, prefixes like "sk-", "ghp_", "AIza") are suspicious.
- Database connections with inline passwords (postgres://user:password@host) are violations.
