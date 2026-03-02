# Padroes de Pull Request

## Tamanho
- PRs devem ter no maximo 400 linhas de codigo alterado (excluindo arquivos gerados).
- PRs grandes devem ser divididos em PRs menores e independentes.

## Descricao
- Todo PR deve ter descricao explicando O QUE foi feito e POR QUE.
- PRs sem descricao devem ser rejeitados.
- Incluir link para issue/ticket relacionado quando aplicavel.

## Reviewers
- Todo PR deve ter pelo menos 1 reviewer aprovado antes do merge.
- PRs que alteram infraestrutura (Terraform, Dockerfile, CI/CD) precisam de 2 reviewers.
- O autor do PR nao pode aprovar o proprio PR.

## Commits
- Mensagens de commit devem ser descritivas (nao usar "fix", "update", "wip" sozinhos).
- Usar conventional commits quando possivel (feat:, fix:, chore:, docs:).
