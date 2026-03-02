# Compliance and Data Protection

## Privacy and Personal Data (PII)
- Personal data (PII) must not be logged in plain text.
- Sensitive fields (email, phone, national ID) must be masked in logs and API responses.
- Personal data must have a defined retention policy — do not store indefinitely.
- User consent must be collected before processing personal data.

## Data Retention
- Application logs: maximum retention of 90 days in production.
- Deleted user data must be removed from all backends within 30 days.
- Backups containing personal data must follow the same retention policy.

## Audit Trail
- Administrative actions must generate an audit record (who, when, what).
- Access to sensitive data must be logged with user identification.
