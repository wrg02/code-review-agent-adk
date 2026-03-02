# Architecture — Governance Agent ADK

## Overview

A multi-agent governance system built with the Google ADK (Agent Development Kit). Replaces Agentspace (Gemini Enterprise) with a solution that has no enterprise license dependency.

A single Cloud Run service handles any client: Cloud Build (PR review), Slack, CLI, Jira, etc.

## Architecture

```
Any Client (Cloud Build, Slack, CLI, Jira)
        |
        |  POST /query  {"input": "...", "context": {...}}
        |  POST /review {"diff": "..."}
        v
Cloud Run (single service, scale-to-zero)
        |
        v
  Root Agent ("governance_agent")
        |
        |--- delegates --> governance_rules_agent
        |                    tools: [load_governance_rules]
        |
        |--- delegates --> security_agent
        |                    tools: [load_security_rules]
        |
        |--- delegates --> code_quality_agent
        |                    tools: [load_code_quality_rules]
        |
        v
  Consolidated response → JSON to client
```

## Endpoints

| Endpoint | Method | Usage |
|----------|--------|-------|
| `/health` | GET | Health check |
| `/query` | POST | Generic endpoint (Slack, CLI, free-form questions) |
| `/review` | POST | PR review (Cloud Build) |

### POST /query

```json
// Request
{"input": "What are the naming convention rules?", "context": {}}

// Response
{"response": "According to naming_conventions.md..."}
```

### POST /review

```json
// Request
{"diff": "+password = 'abc123'"}

// Response
{
  "approved": false,
  "violations": ["Hardcoded password detected"],
  "recommendation": "Use Secret Manager",
  "feedback_md": "## Governance Review..."
}
```

## Sub-Agents

| Agent | Domain | Tool | GCS Prefix |
|-------|--------|------|------------|
| governance_rules_agent | Compliance, PR standards, branching | load_governance_rules | governance/ |
| security_agent | Secrets, OWASP, vulnerabilities | load_security_rules | security/ |
| code_quality_agent | Naming, error handling, testing | load_code_quality_rules | code-quality/ |

## Rules

Rules live in GCS (bucket configured via `RULES_BUCKET`), organized by domain:

```
gs://governance-rules-<project>/
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

For local development, set `LOCAL_RULES_DIR=rules/`.

## File Structure

```
code-review-agent-adk/
├── governance_agent/
│   ├── __init__.py
│   ├── agent.py                  # Root agent with sub_agents
│   ├── app.py                    # Flask: /query + /review + /health
│   ├── static/
│   │   └── index.html            # Chat UI
│   ├── sub_agents/
│   │   ├── __init__.py
│   │   ├── governance.py
│   │   ├── security.py
│   │   └── code_quality.py
│   └── tools/
│       ├── __init__.py
│       └── gcs_reader.py
├── rules/                        # Local copies (dev/testing)
├── cloudbuild.yaml               # PR review pipeline
├── Dockerfile
├── requirements.txt
├── tests/
└── docs/
    ├── architecture.md
    └── architecture.mmd
```

## Cloud Build (PR Review)

The `cloudbuild.yaml` pipeline:
1. Generates the PR diff (`git diff`)
2. Calls `POST /review` on Cloud Run with an identity token
3. Posts `feedback_md` as a comment on the GitHub PR via API
4. Fails the build if the PR is rejected (`approved: false`)

Required substitutions: `_AGENT_URL`, `_GITHUB_REPO`, `_PR_NUMBER`.

## Extensibility

To add a new domain (e.g., "Cost Optimization"):
1. Create `sub_agents/cost_optimization.py` with an ADK Agent
2. Add `load_cost_rules()` to `gcs_reader.py`
3. Register the sub-agent in `agent.py`
4. Upload rules to `gs://bucket/cost-optimization/`

Zero changes to the API, Dockerfile, or Cloud Build pipeline.

## Comparison: Agentspace vs ADK

| Aspect | Agentspace | ADK Multi-Agent |
|--------|------------|-----------------|
| Services | Cloud Run + Agentspace | 1 Cloud Run |
| AI Engine | Gemini Enterprise | Gemini API (via ADK) |
| Rules | Agentspace data store | GCS (markdown files) |
| Dependency | Enterprise license | Open-source SDK |
| Cost | License + API | Gemini API + GCS |
| Extensibility | Limited | Unlimited sub-agents |
| Clients | Pipeline-coupled | Any HTTP client |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Agent framework | Google ADK |
| AI model | Gemini Flash |
| HTTP server | Flask + Gunicorn |
| Runtime | Cloud Run (scale-to-zero) |
| Rules storage | Cloud Storage (GCS) |
| CI/CD | Cloud Build |
| Authentication | IAM (identity token) |

## Deployment Prerequisites

1. GCP project with billing enabled
2. APIs enabled: Cloud Run, Cloud Storage, Vertex AI
3. GCS bucket with rule documents
4. Service Account with permissions:
   - `storage.objects.get` and `storage.objects.list` on the bucket
   - `aiplatform.endpoints.predict` for Gemini
5. `github-pat` secret in Secret Manager (for Cloud Build)
6. Environment variables: `RULES_BUCKET`, `PORT`
