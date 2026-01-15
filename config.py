"""
Configuration module that handles secrets from either:
- Google Cloud Secret Manager (in production/Cloud Run)
- Local .env file (in development)
"""
import os
from functools import lru_cache


def _get_secret_from_gcp(secret_id: str, project_id: str | None = None) -> str | None:
    """Fetch a secret from Google Cloud Secret Manager."""
    try:
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()

        # Use project ID from env or let GCP auto-detect
        if project_id is None:
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")

        if not project_id:
            return None

        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception:
        return None


def _get_secret_from_env(key: str) -> str | None:
    """Fetch a secret from environment variables or .env file."""
    from dotenv import load_dotenv
    load_dotenv()
    return os.environ.get(key)


@lru_cache()
def get_openai_api_key() -> str:
    """
    Get OpenAI API key from the best available source.

    Priority:
    1. OPENAI_API_KEY environment variable (already set)
    2. Google Cloud Secret Manager (if running in GCP)
    3. Local .env file
    """
    # Check if already in environment
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    # Try Google Cloud Secret Manager
    key = _get_secret_from_gcp("openai-api-key")
    if key:
        os.environ["OPENAI_API_KEY"] = key
        return key

    # Fall back to .env file
    key = _get_secret_from_env("OPENAI_API_KEY")
    if key:
        return key

    raise ValueError(
        "OPENAI_API_KEY not found. Set it via environment variable, "
        "Google Cloud Secret Manager, or .env file."
    )


def is_running_in_cloud() -> bool:
    """Check if running in a cloud environment (Cloud Run, App Engine, etc.)."""
    return any([
        os.environ.get("K_SERVICE"),  # Cloud Run
        os.environ.get("GAE_ENV"),     # App Engine
        os.environ.get("GOOGLE_CLOUD_PROJECT"),
    ])
