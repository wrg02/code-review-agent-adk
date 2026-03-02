from google.adk.agents import Agent

from governance_agent.tools.gcs_reader import load_governance_rules

governance_rules_agent = Agent(
    name="governance_rules_agent",
    model="gemini-3-flash-preview",
    instruction="""You are a software governance expert.

Your responsibilities:
1. Use the 'load_governance_rules' tool to load the governance rules.
2. Analyze the user's input against EACH loaded rule.
3. For each violation found, cite the source document (file name).
4. If no violations are found, confirm compliance.

Always load the rules before performing the analysis. Be specific when citing sources.""",
    tools=[load_governance_rules],
)
