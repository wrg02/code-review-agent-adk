import unittest

from governance_agent.agent import root_agent
from governance_agent.sub_agents.governance import governance_rules_agent
from governance_agent.sub_agents.security import security_agent
from governance_agent.sub_agents.code_quality import code_quality_agent


class TestAgentStructure(unittest.TestCase):
    def test_root_agent_exists(self):
        self.assertEqual(root_agent.name, "governance_agent")

    def test_root_agent_has_sub_agents(self):
        sub_agent_names = [a.name for a in root_agent.sub_agents]
        self.assertIn("governance_rules_agent", sub_agent_names)
        self.assertIn("security_agent", sub_agent_names)
        self.assertIn("code_quality_agent", sub_agent_names)

    def test_governance_agent_has_tools(self):
        tool_names = [t.__name__ for t in governance_rules_agent.tools]
        self.assertIn("load_governance_rules", tool_names)

    def test_security_agent_has_tools(self):
        tool_names = [t.__name__ for t in security_agent.tools]
        self.assertIn("load_security_rules", tool_names)

    def test_code_quality_agent_has_tools(self):
        tool_names = [t.__name__ for t in code_quality_agent.tools]
        self.assertIn("load_code_quality_rules", tool_names)

    def test_all_agents_use_same_model(self):
        model = root_agent.model
        self.assertIsNotNone(model)
        self.assertEqual(governance_rules_agent.model, model)
        self.assertEqual(security_agent.model, model)
        self.assertEqual(code_quality_agent.model, model)


if __name__ == "__main__":
    unittest.main()
