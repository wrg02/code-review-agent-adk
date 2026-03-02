import os
import glob as glob_mod


RULES_BUCKET = os.environ.get("RULES_BUCKET", "")
LOCAL_RULES_DIR = os.environ.get("LOCAL_RULES_DIR", "")


def _read_rules_from_gcs(bucket: str, prefix: str) -> str:
    """List blobs under the given GCS prefix, filter .md/.txt files, and concatenate their content."""
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
        return f"No rules found under prefix '{prefix}'."
    return "\n\n".join(parts)


def _read_rules_local(base_dir: str, prefix: str) -> str:
    """Read rules from a local directory (for development and testing)."""
    rules_path = os.path.join(base_dir, prefix)
    if not os.path.isdir(rules_path):
        return f"Rules directory not found: {rules_path}"

    parts = []
    for filepath in sorted(glob_mod.glob(os.path.join(rules_path, "**/*"), recursive=True)):
        if filepath.endswith((".md", ".txt")) and os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            parts.append(f"--- {filename} ---\n{content}")

    if not parts:
        return f"No rules found in '{rules_path}'."
    return "\n\n".join(parts)


def _load_rules(prefix: str) -> str:
    """Load rules from GCS or local directory depending on configuration."""
    if LOCAL_RULES_DIR:
        return _read_rules_local(LOCAL_RULES_DIR, prefix)
    if RULES_BUCKET:
        return _read_rules_from_gcs(RULES_BUCKET, prefix)
    return "Error: neither RULES_BUCKET nor LOCAL_RULES_DIR is configured."


def load_governance_rules() -> str:
    """Load governance rules (compliance, PR standards, branching strategy).

    Returns the concatenated content of all governance rule documents.
    """
    return _load_rules("governance/")


def load_security_rules() -> str:
    """Load security rules (secrets management, OWASP, dependencies, APIs).

    Returns the concatenated content of all security rule documents.
    """
    return _load_rules("security/")


def load_code_quality_rules() -> str:
    """Load code quality rules (naming conventions, error handling, testing).

    Returns the concatenated content of all code quality rule documents.
    """
    return _load_rules("code-quality/")
