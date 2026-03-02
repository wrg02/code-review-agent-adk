# Naming Conventions

## Python
- Variables and functions: snake_case (e.g., user_name, get_user_by_id)
- Classes: PascalCase (e.g., UserService, DatabaseConnection)
- Constants: UPPER_SNAKE_CASE (e.g., MAX_RETRIES, DEFAULT_TIMEOUT)
- Modules and packages: snake_case (e.g., user_service.py, data_pipeline/)
- Private variables: underscore prefix (e.g., _internal_cache)

## General
- Names must be descriptive — avoid obscure abbreviations (use "connection" instead of "conn").
- Functions must start with a verb (get_, create_, update_, delete_, is_, has_).
- Booleans must have an indicative prefix (is_active, has_permission, can_edit).
- Avoid generic names (data, info, temp, result) except in very short scopes.
- File names must reflect the main content they contain.

## Consistency
- Use the same term for the same concept throughout the project.
- Do not mix languages in variable names within the same module.
