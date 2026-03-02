# Error Handling

## Principles
- Never silence exceptions with `except: pass` or `except Exception: pass` without logging.
- Catch specific exceptions — avoid bare `except Exception` when possible.
- Log errors with enough context for diagnosis (stack trace, relevant parameters).
- Fail gracefully — return useful error messages to the user without exposing internal details.

## APIs and Endpoints
- Return appropriate HTTP status codes (400 for invalid input, 401/403 for auth, 500 for internal errors).
- Error responses must have a consistent format (e.g., {"error": "message", "code": "ERROR_CODE"}).
- Never return stack traces or internal messages in production API responses.

## Logging
- Use appropriate log levels: ERROR for errors, WARNING for anomalous situations, INFO for normal flow.
- Include correlation ID / request ID in logs for traceability.
- Do not log sensitive data (passwords, tokens, PII) in error messages.

## Retry and Resilience
- Network operations must have a configured timeout.
- Implement retry with exponential backoff for calls to external services.
- Define a circuit breaker for critical dependencies.
