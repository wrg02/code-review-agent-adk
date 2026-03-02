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
    """Executa o agente com o input do usuario e retorna a resposta final."""
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
    """Extrai um objeto JSON de texto que pode conter markdown."""
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
    """Gera o Markdown de feedback a partir do resultado da revisao."""
    lines = ["## Review de Governanca (ADK Multi-Agent)\n"]
    if result.get("aprovado"):
        lines.append("**Status: Aprovado**\n")
        lines.append("O codigo esta em conformidade com as diretrizes configuradas.\n")
    else:
        lines.append("**Status: Bloqueado**\n")
        lines.append("Foram encontradas as seguintes violacoes:\n")
        for violacao in result.get("violacoes", []):
            lines.append(f"- {violacao}")
        recomendacao = result.get("recomendacao", "")
        if recomendacao:
            lines.append(f"\n**Recomendacao Corretiva:**\n> {recomendacao}\n")
    return "\n".join(lines)


@app.route("/", methods=["GET"])
def index():
    return send_from_directory("static", "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/query", methods=["POST"])
async def query():
    """Endpoint generico para qualquer cliente (Slack, CLI, Cloud Build, etc.)."""
    body = request.get_json(force=True)
    user_input = body.get("input", "")
    context = body.get("context", {})

    if not user_input.strip():
        return jsonify({"error": "Campo 'input' vazio ou ausente."}), 400

    if context:
        user_input += f"\n\nContexto adicional:\n{json.dumps(context, ensure_ascii=False, indent=2)}"

    response_text = await _run_agent(user_input)

    return jsonify({"response": response_text}), 200


@app.route("/review", methods=["POST"])
async def review():
    """Endpoint de conveniencia para PR review (Cloud Build)."""
    body = request.get_json(force=True)
    diff = body.get("diff", "")

    if not diff.strip():
        return jsonify({"error": "Campo 'diff' vazio ou ausente."}), 400

    prompt = f"""Analise o seguinte diff de Pull Request contra TODAS as regras de governanca, seguranca e qualidade de codigo.

Retorne sua analise como um JSON com a seguinte estrutura:
{{
  "aprovado": booleano (true se nenhuma violacao critica, false caso contrario),
  "violacoes": ["lista de violacoes encontradas"],
  "recomendacao": "recomendacao geral para o autor do PR"
}}

Diff do PR:
{diff}"""

    response_text = await _run_agent(prompt)

    try:
        result = _extract_json_from_text(response_text)
    except (json.JSONDecodeError, ValueError):
        return jsonify({
            "aprovado": False,
            "violacoes": [],
            "recomendacao": "",
            "feedback_md": response_text,
            "raw_response": response_text,
        }), 200

    feedback_md = _build_feedback_md(result)

    return jsonify({
        "aprovado": result.get("aprovado", False),
        "violacoes": result.get("violacoes", []),
        "recomendacao": result.get("recomendacao", ""),
        "feedback_md": feedback_md,
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
