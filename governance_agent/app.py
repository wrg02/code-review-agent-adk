import os
import json
import re

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from governance_agent.agent import root_agent

app = Flask(__name__)

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="governance_app", session_service=session_service)


async def _run_agent(user_input: str) -> str:
    """Run the agent with the given input and return the final response."""
    session = await session_service.create_session(
        app_name="governance_app", user_id="api_user"
    )

    user_message = types.Content(
        role="user", parts=[types.Part.from_text(text=user_input)]
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="api_user", session_id=session.id, new_message=user_message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = "\n".join(
                part.text for part in event.content.parts if part.text
            )

    return final_response


def _extract_json_from_text(text: str) -> dict:
    """Extract a JSON object from text that may contain markdown code fences."""
    clean = text.strip()
    if "```json" in clean:
        clean = clean.split("```json")[1].split("```")[0]
    elif "```" in clean:
        clean = clean.split("```")[1].split("```")[0]

    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        return json.loads(match.group(0).strip())

    return json.loads(clean)


def _build_feedback_md(result: dict) -> str:
    """Build a Markdown feedback message from the review result."""
    lines = ["## Governance Review (ADK Multi-Agent)\n"]
    if result.get("approved"):
        lines.append("**Status: Approved**\n")
        lines.append("The code complies with all configured governance guidelines.\n")
    else:
        lines.append("**Status: Blocked**\n")
        lines.append("The following violations were found:\n")
        for violation in result.get("violations", []):
            lines.append(f"- {violation}")
        recommendation = result.get("recommendation", "")
        if recommendation:
            lines.append(f"\n**Corrective Recommendation:**\n> {recommendation}\n")
    return "\n".join(lines)


@app.route("/", methods=["GET"])
def index():
    return send_from_directory("static", "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/query", methods=["POST"])
async def query():
    """Generic endpoint for any client (Slack, CLI, etc.)."""
    body = request.get_json(force=True)
    user_input = body.get("input", "")
    context = body.get("context", {})

    if not user_input.strip():
        return jsonify({"error": "Field 'input' is empty or missing."}), 400

    if context:
        user_input += f"\n\nAdditional context:\n{json.dumps(context, ensure_ascii=False, indent=2)}"

    response_text = await _run_agent(user_input)

    return jsonify({"response": response_text}), 200


@app.route("/review", methods=["POST"])
async def review():
    """Convenience endpoint for PR review (Cloud Build)."""
    body = request.get_json(force=True)
    diff = body.get("diff", "")

    if not diff.strip():
        return jsonify({"error": "Field 'diff' is empty or missing."}), 400

    prompt = f"""Analyze the following Pull Request diff against ALL governance, security, and code quality rules.

Return your analysis as a JSON object with the following structure:
{{
  "approved": boolean (true if no critical violations, false otherwise),
  "violations": ["list of violations found"],
  "recommendation": "overall recommendation for the PR author"
}}

PR Diff:
{diff}"""

    response_text = await _run_agent(prompt)

    try:
        result = _extract_json_from_text(response_text)
    except (json.JSONDecodeError, ValueError):
        return jsonify({
            "approved": False,
            "violations": [],
            "recommendation": "",
            "feedback_md": response_text,
            "raw_response": response_text,
        }), 200

    feedback_md = _build_feedback_md(result)

    return jsonify({
        "approved": result.get("approved", False),
        "violations": result.get("violations", []),
        "recommendation": result.get("recommendation", ""),
        "feedback_md": feedback_md,
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
