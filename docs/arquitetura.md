# Arquitetura — Governance Agent ADK

## Visao Geral

Agente de governanca multi-agent construido com Google ADK (Agent Development Kit). Substitui o Agentspace (Gemini Enterprise) por uma solucao sem dependencia de licenca enterprise.

Um unico Cloud Run serve qualquer cliente: Cloud Build (PR review), Slack, CLI, Jira, etc.

## Arquitetura

```
Qualquer Cliente (Cloud Build, Slack, CLI, Jira)
        |
        |  POST /query  {"input": "...", "context": {...}}
        |  POST /review {"diff": "..."}
        v
Cloud Run (unico, scale-to-zero)
        |
        v
  Root Agent ("governance_agent")
        |
        |--- delega ---> governance_rules_agent
        |                  tools: [load_governance_rules]
        |
        |--- delega ---> security_agent
        |                  tools: [load_security_rules]
        |
        |--- delega ---> code_quality_agent
        |                  tools: [load_code_quality_rules]
        |
        v
  Resposta consolidada → JSON pro cliente
```

## Endpoints

| Endpoint | Metodo | Uso |
|----------|--------|-----|
| `/health` | GET | Health check |
| `/query` | POST | Consulta generica (Slack, CLI, etc.) |
| `/review` | POST | PR review (Cloud Build) |

### POST /query

```json
// Request
{"input": "Quais sao as regras de naming conventions?", "context": {}}

// Response
{"response": "De acordo com naming_conventions.md..."}
```

### POST /review

```json
// Request
{"diff": "+password = 'abc123'"}

// Response
{
  "aprovado": false,
  "violacoes": ["Hardcoded password detectado"],
  "recomendacao": "Usar Secret Manager",
  "feedback_md": "## Review de Governanca..."
}
```

## Sub-Agentes

| Agente | Dominio | Tool | Prefixo GCS |
|--------|---------|------|-------------|
| governance_rules_agent | Compliance, padroes de PR, branching | load_governance_rules | governance/ |
| security_agent | Secrets, OWASP, vulnerabilidades | load_security_rules | security/ |
| code_quality_agent | Naming, error handling, testes | load_code_quality_rules | code-quality/ |

## Regras

Regras vivem em GCS (bucket configurado via `RULES_BUCKET`) organizadas por dominio:

```
gs://governance-rules-<projeto>/
├── governance/
│   ├── compliance.md
│   ├── pr_standards.md
│   └── branching_strategy.md
├── security/
│   ├── secrets_management.md
│   ├── owasp_top10.md
│   ├── dependency_policy.md
│   └── api_security.md
└── code-quality/
    ├── naming_conventions.md
    ├── error_handling.md
    ├── testing_standards.md
    └── documentation.md
```

Para desenvolvimento local, usar `LOCAL_RULES_DIR=regras/`.

## Estrutura de Arquivos

```
code-review-agent-adk/
├── governance_agent/
│   ├── __init__.py
│   ├── agent.py                  # Root agent com sub_agents
│   ├── app.py                    # Flask: /query + /review + /health
│   ├── sub_agents/
│   │   ├── __init__.py
│   │   ├── governance.py
│   │   ├── security.py
│   │   └── code_quality.py
│   └── tools/
│       ├── __init__.py
│       └── gcs_reader.py
├── regras/                       # Copias locais (dev/testes)
├── cloudbuild.yaml               # Pipeline de PR review
├── Dockerfile
├── requirements.txt
├── tests/
└── docs/
    └── arquitetura.md
```

## Cloud Build (PR Review)

O `cloudbuild.yaml` implementa o pipeline:
1. Gera diff do PR (`git diff`)
2. Chama `POST /review` no Cloud Run com identity token
3. Posta `feedback_md` como comentario no GitHub via API
4. Falha o build se PR reprovado (`aprovado: false`)

Substituicoes obrigatorias: `_AGENT_URL`, `_GITHUB_REPO`, `_PR_NUMBER`.

## Extensibilidade

Adicionar novo dominio (ex: "Cost Optimization"):
1. Criar `sub_agents/cost_optimization.py` com Agent ADK
2. Adicionar `load_cost_rules()` em `gcs_reader.py`
3. Registrar sub-agente em `agent.py`
4. Upload de regras em `gs://bucket/cost-optimization/`

Zero mudanca na API, Dockerfile ou Cloud Build.

## Comparativo: Agentspace vs ADK

| Aspecto | Agentspace | ADK Multi-Agent |
|---------|------------|-----------------|
| Servicos | Cloud Run + Agentspace | 1 Cloud Run |
| Motor de IA | Gemini Enterprise | Gemini API (via ADK) |
| Regras | Data store no Agentspace | GCS (markdown) |
| Dependencia | Licenca enterprise | SDK open-source |
| Custo | Licenca + API | API Gemini + GCS |
| Extensibilidade | Limitada | Sub-agentes ilimitados |
| Clientes | Acoplado ao pipeline | Qualquer HTTP client |

## Tecnologias

| Componente | Tecnologia |
|------------|------------|
| Framework de agentes | Google ADK |
| Modelo de IA | Gemini 2.0 Flash |
| HTTP | Flask + Gunicorn |
| Runtime | Cloud Run (scale-to-zero) |
| Regras | Cloud Storage (GCS) |
| CI/CD | Cloud Build |
| Autenticacao | IAM (identity token) |

## Pre-requisitos para Deploy

1. Projeto GCP com billing ativo
2. APIs habilitadas: Cloud Run, Cloud Storage, Vertex AI
3. Bucket GCS com documentos de regras
4. Service Account com permissoes:
   - `storage.objects.get` e `storage.objects.list` no bucket
   - `aiplatform.endpoints.predict` para Gemini
5. Secret `github-pat` no Secret Manager (para Cloud Build)
6. Variaveis de ambiente: `RULES_BUCKET`, `PORT`
