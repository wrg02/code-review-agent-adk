from google.adk.agents import Agent

from governance_agent.sub_agents.governance import governance_rules_agent
from governance_agent.sub_agents.security import security_agent
from governance_agent.sub_agents.code_quality import code_quality_agent

root_agent = Agent(
    name="governance_agent",
    model='gemini-3-flash-preview',
    instruction="""Voce e o agente principal de governanca de software. Voce coordena sub-agentes especializados para analisar codigo, PRs e responder perguntas sobre governanca.

Regras de delegacao:
- Para DIFFS de Pull Request ou revisoes de codigo: delegue para TODOS os sub-agentes (governance_rules_agent, security_agent, code_quality_agent) e consolide os resultados.
- Para perguntas sobre compliance, padroes de PR ou branching: delegue para governance_rules_agent.
- Para perguntas sobre seguranca, secrets ou vulnerabilidades: delegue para security_agent.
- Para perguntas sobre qualidade de codigo, naming ou testes: delegue para code_quality_agent.
- Para perguntas gerais que possam envolver multiplos dominios: delegue para os sub-agentes relevantes.

Ao consolidar respostas de multiplos sub-agentes:
1. Apresente os resultados organizados por dominio (Governanca, Seguranca, Qualidade).
2. Destaque violacoes criticas primeiro.
3. Forneca um resumo geral no final.

Responda sempre em portugues.""",
    sub_agents=[governance_rules_agent, security_agent, code_quality_agent],
)
