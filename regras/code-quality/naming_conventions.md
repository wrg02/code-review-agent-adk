# Convencoes de Nomenclatura

## Python
- Variaveis e funcoes: snake_case (ex: user_name, get_user_by_id)
- Classes: PascalCase (ex: UserService, DatabaseConnection)
- Constantes: UPPER_SNAKE_CASE (ex: MAX_RETRIES, DEFAULT_TIMEOUT)
- Modulos e pacotes: snake_case (ex: user_service.py, data_pipeline/)
- Variaveis privadas: prefixo underscore (ex: _internal_cache)

## Geral
- Nomes devem ser descritivos — evitar abreviacoes obscuras (usar "connection" ao inves de "conn").
- Funcoes devem comecar com verbo (get_, create_, update_, delete_, is_, has_).
- Booleanos devem ter prefixo indicativo (is_active, has_permission, can_edit).
- Evitar nomes genericos (data, info, temp, result) exceto em escopos muito curtos.
- Nomes de arquivos devem refletir o conteudo principal.

## Consistencia
- Usar o mesmo termo para o mesmo conceito em todo o projeto.
- Nao misturar idiomas (portugues e ingles) em nomes de variaveis no mesmo modulo.
