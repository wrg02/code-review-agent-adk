import os
import glob as glob_mod


RULES_BUCKET = os.environ.get("RULES_BUCKET", "")
LOCAL_RULES_DIR = os.environ.get("LOCAL_RULES_DIR", "")


def _read_rules_from_gcs(bucket: str, prefix: str) -> str:
    """Lista blobs no prefixo do bucket GCS, filtra .md/.txt e concatena conteudo."""
    from google.cloud import storage

    client = storage.Client()
    bucket_obj = client.bucket(bucket)
    blobs = bucket_obj.list_blobs(prefix=prefix)

    parts = []
    for blob in blobs:
        if blob.name.endswith((".md", ".txt")):
            content = blob.download_as_text()
            filename = blob.name.split("/")[-1]
            parts.append(f"--- {filename} ---\n{content}")

    if not parts:
        return f"Nenhuma regra encontrada no prefixo '{prefix}'."
    return "\n\n".join(parts)


def _read_rules_local(base_dir: str, prefix: str) -> str:
    """Le regras de um diretorio local (para desenvolvimento e testes)."""
    rules_path = os.path.join(base_dir, prefix)
    if not os.path.isdir(rules_path):
        return f"Diretorio de regras nao encontrado: {rules_path}"

    parts = []
    for filepath in sorted(glob_mod.glob(os.path.join(rules_path, "**/*"), recursive=True)):
        if filepath.endswith((".md", ".txt")) and os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            parts.append(f"--- {filename} ---\n{content}")

    if not parts:
        return f"Nenhuma regra encontrada em '{rules_path}'."
    return "\n\n".join(parts)


def _load_rules(prefix: str) -> str:
    """Carrega regras do GCS ou local, dependendo da configuracao."""
    if LOCAL_RULES_DIR:
        return _read_rules_local(LOCAL_RULES_DIR, prefix)
    if RULES_BUCKET:
        return _read_rules_from_gcs(RULES_BUCKET, prefix)
    return "Erro: nem RULES_BUCKET nem LOCAL_RULES_DIR estao configurados."


def load_governance_rules() -> str:
    """Carrega as regras de governanca (compliance, padroes de PR, branching).

    Retorna o conteudo concatenado de todos os documentos de governanca.
    """
    return _load_rules("governance/")


def load_security_rules() -> str:
    """Carrega as regras de seguranca (secrets, OWASP, dependencias, APIs).

    Retorna o conteudo concatenado de todos os documentos de seguranca.
    """
    return _load_rules("security/")


def load_code_quality_rules() -> str:
    """Carrega as regras de qualidade de codigo (naming, error handling, testes).

    Retorna o conteudo concatenado de todos os documentos de qualidade de codigo.
    """
    return _load_rules("code-quality/")
