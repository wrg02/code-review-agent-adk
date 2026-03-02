# Compliance e Protecao de Dados

## LGPD e Privacidade
- Dados pessoais (PII) nao devem ser logados em texto plano.
- Campos sensiveis (CPF, email, telefone) devem ser mascarados em logs e respostas de API.
- Dados pessoais devem ter politica de retencao definida — nao armazenar indefinidamente.
- Consentimento do usuario deve ser coletado antes de processar dados pessoais.

## Retencao de Dados
- Logs de aplicacao: retencao maxima de 90 dias em ambiente de producao.
- Dados de usuario excluidos devem ser removidos de todos os backends em ate 30 dias.
- Backups contendo dados pessoais devem seguir a mesma politica de retencao.

## Auditoria
- Acoes administrativas devem gerar registro de auditoria (quem, quando, o que).
- Acessos a dados sensiveis devem ser logados com identificacao do usuario.
