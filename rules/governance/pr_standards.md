# Pull Request Standards

## Size
- PRs must have at most 400 changed lines of code (excluding generated files).
- Large PRs must be split into smaller, independent PRs.

## Description
- Every PR must have a description explaining WHAT was done and WHY.
- PRs without a description must be rejected.
- Include a link to the related issue/ticket when applicable.

## Reviewers
- Every PR must have at least 1 approved reviewer before merging.
- PRs that change infrastructure (Terraform, Dockerfile, CI/CD) require 2 reviewers.
- The PR author cannot approve their own PR.

## Commits
- Commit messages must be descriptive (do not use "fix", "update", "wip" alone).
- Use conventional commits when possible (feat:, fix:, chore:, docs:).
