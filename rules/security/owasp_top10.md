# OWASP Top 10 — Security Rules

## A01: Broken Access Control
- Validate authorization on ALL endpoints (not just authentication).
- Do not trust client-supplied data for authorization decisions.
- Implement the principle of least privilege.

## A02: Cryptographic Failures
- Use HTTPS for all external communications.
- Do not use deprecated cryptographic algorithms (MD5, SHA1 for password hashing).
- Use bcrypt, scrypt, or Argon2 for password hashing.

## A03: Injection
- Use parameterized queries (prepared statements) — NEVER concatenate user input into SQL.
- Sanitize user input before using it in system commands (OS command injection).
- Validate and sanitize input in templates (Server-Side Template Injection).

## A04: Insecure Design
- Implement rate limiting on authentication endpoints.
- Validate input on the backend (do not rely solely on frontend validation).

## A05: Security Misconfiguration
- Do not expose stack traces or detailed error messages in production.
- Disable unnecessary headers that reveal technology (X-Powered-By).
- Configure CORS restrictively (do not use wildcard * in production).

## A07: Cross-Site Scripting (XSS)
- Escape output in HTML, JavaScript, and URL contexts.
- Use Content Security Policy (CSP) headers.

## A08: Software and Data Integrity Failures
- Verify dependency integrity (checksums, lock files).
- Do not deserialize data from untrusted sources without validation.

## A09: Security Logging and Monitoring
- Log failed authentication attempts.
- Implement alerts for anomalous activity.
