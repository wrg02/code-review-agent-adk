import json
import unittest
from unittest.mock import patch


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        from governance_agent.app import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "ok")

    def test_query_empty_input(self):
        response = self.client.post(
            "/query",
            data=json.dumps({"input": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_review_empty_diff(self):
        response = self.client.post(
            "/review",
            data=json.dumps({"diff": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    @patch("governance_agent.app._run_agent")
    def test_query_success(self, mock_run):
        mock_run.return_value = "Analysis complete. No violations found."
        response = self.client.post(
            "/query",
            data=json.dumps({"input": "Check this code: print('hello')"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("response", data)
        self.assertEqual(data["response"], "Analysis complete. No violations found.")

    @patch("governance_agent.app._run_agent")
    def test_query_with_context(self, mock_run):
        mock_run.return_value = "Analysis with context."
        response = self.client.post(
            "/query",
            data=json.dumps({
                "input": "Analyze this PR",
                "context": {"repo": "my-repo", "pr_number": 42},
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        call_args = mock_run.call_args[0][0]
        self.assertIn("my-repo", call_args)
        self.assertIn("42", call_args)

    @patch("governance_agent.app._run_agent")
    def test_review_success_approved(self, mock_run):
        mock_run.return_value = json.dumps({
            "approved": True,
            "violations": [],
            "recommendation": "Code looks good.",
        })
        response = self.client.post(
            "/review",
            data=json.dumps({"diff": "+print('hello')"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["approved"])
        self.assertEqual(data["violations"], [])
        self.assertIn("Approved", data["feedback_md"])

    @patch("governance_agent.app._run_agent")
    def test_review_success_rejected(self, mock_run):
        mock_run.return_value = json.dumps({
            "approved": False,
            "violations": ["Hardcoded password detected"],
            "recommendation": "Use Secret Manager.",
        })
        response = self.client.post(
            "/review",
            data=json.dumps({"diff": "+password = 'abc123'"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["approved"])
        self.assertIn("Hardcoded password detected", data["violations"])
        self.assertIn("Blocked", data["feedback_md"])

    @patch("governance_agent.app._run_agent")
    def test_review_non_json_response(self, mock_run):
        mock_run.return_value = "Response without structured JSON."
        response = self.client.post(
            "/review",
            data=json.dumps({"diff": "+some code"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["approved"])
        self.assertIn("raw_response", data)


if __name__ == "__main__":
    unittest.main()
