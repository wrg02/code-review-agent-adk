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
        mock_run.return_value = "Analise completa. Sem violacoes."
        response = self.client.post(
            "/query",
            data=json.dumps({"input": "Verifique este codigo: print('hello')"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("response", data)
        self.assertEqual(data["response"], "Analise completa. Sem violacoes.")

    @patch("governance_agent.app._run_agent")
    def test_query_with_context(self, mock_run):
        mock_run.return_value = "Analise com contexto."
        response = self.client.post(
            "/query",
            data=json.dumps({
                "input": "Analise este PR",
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
            "aprovado": True,
            "violacoes": [],
            "recomendacao": "Codigo OK.",
        })
        response = self.client.post(
            "/review",
            data=json.dumps({"diff": "+print('hello')"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["aprovado"])
        self.assertEqual(data["violacoes"], [])
        self.assertIn("Aprovado", data["feedback_md"])

    @patch("governance_agent.app._run_agent")
    def test_review_success_rejected(self, mock_run):
        mock_run.return_value = json.dumps({
            "aprovado": False,
            "violacoes": ["Hardcoded password detectado"],
            "recomendacao": "Usar Secret Manager.",
        })
        response = self.client.post(
            "/review",
            data=json.dumps({"diff": "+password = 'abc123'"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["aprovado"])
        self.assertIn("Hardcoded password detectado", data["violacoes"])
        self.assertIn("Bloqueado", data["feedback_md"])

    @patch("governance_agent.app._run_agent")
    def test_review_non_json_response(self, mock_run):
        mock_run.return_value = "Resposta sem JSON estruturado."
        response = self.client.post(
            "/review",
            data=json.dumps({"diff": "+some code"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["aprovado"])
        self.assertIn("raw_response", data)


if __name__ == "__main__":
    unittest.main()
