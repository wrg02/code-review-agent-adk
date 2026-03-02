import os
import unittest
from unittest.mock import patch, MagicMock

from governance_agent.tools.gcs_reader import (
    _read_rules_local,
    _load_rules,
    load_governance_rules,
    load_security_rules,
    load_code_quality_rules,
)


class TestReadRulesLocal(unittest.TestCase):
    def test_reads_governance_files(self):
        base_dir = os.path.join(os.path.dirname(__file__), "..", "rules")
        result = _read_rules_local(base_dir, "governance/")
        self.assertIn("compliance.md", result)
        self.assertIn("pr_standards.md", result)
        self.assertIn("Compliance", result)

    def test_reads_security_rules(self):
        base_dir = os.path.join(os.path.dirname(__file__), "..", "rules")
        result = _read_rules_local(base_dir, "security/")
        self.assertIn("secrets_management.md", result)
        self.assertIn("owasp_top10.md", result)

    def test_reads_code_quality_rules(self):
        base_dir = os.path.join(os.path.dirname(__file__), "..", "rules")
        result = _read_rules_local(base_dir, "code-quality/")
        self.assertIn("naming_conventions.md", result)
        self.assertIn("error_handling.md", result)

    def test_missing_directory(self):
        result = _read_rules_local("/tmp", "nonexistent/")
        self.assertIn("not found", result)


class TestLoadRulesWithLocalDir(unittest.TestCase):
    def test_no_config_returns_error(self):
        from governance_agent.tools import gcs_reader
        original_local = gcs_reader.LOCAL_RULES_DIR
        original_bucket = gcs_reader.RULES_BUCKET
        gcs_reader.LOCAL_RULES_DIR = ""
        gcs_reader.RULES_BUCKET = ""
        try:
            result = _load_rules("governance/")
            self.assertIn("Error", result)
        finally:
            gcs_reader.LOCAL_RULES_DIR = original_local
            gcs_reader.RULES_BUCKET = original_bucket


class TestLoadRulesFromGCS(unittest.TestCase):
    @patch("governance_agent.tools.gcs_reader._read_rules_from_gcs")
    def test_gcs_called_when_bucket_set(self, mock_gcs):
        from governance_agent.tools import gcs_reader
        original_local = gcs_reader.LOCAL_RULES_DIR
        original_bucket = gcs_reader.RULES_BUCKET
        gcs_reader.LOCAL_RULES_DIR = ""
        gcs_reader.RULES_BUCKET = "my-bucket"
        mock_gcs.return_value = "rules from gcs"
        try:
            result = _load_rules("governance/")
            mock_gcs.assert_called_once_with("my-bucket", "governance/")
            self.assertEqual(result, "rules from gcs")
        finally:
            gcs_reader.LOCAL_RULES_DIR = original_local
            gcs_reader.RULES_BUCKET = original_bucket


class TestDomainFunctions(unittest.TestCase):
    @patch("governance_agent.tools.gcs_reader._load_rules")
    def test_load_governance_rules(self, mock_load):
        mock_load.return_value = "governance content"
        load_governance_rules()
        mock_load.assert_called_with("governance/")

    @patch("governance_agent.tools.gcs_reader._load_rules")
    def test_load_security_rules(self, mock_load):
        mock_load.return_value = "security content"
        load_security_rules()
        mock_load.assert_called_with("security/")

    @patch("governance_agent.tools.gcs_reader._load_rules")
    def test_load_code_quality_rules(self, mock_load):
        mock_load.return_value = "quality content"
        load_code_quality_rules()
        mock_load.assert_called_with("code-quality/")


if __name__ == "__main__":
    unittest.main()
