import anthropic
import structlog
from flask import current_app

logger = structlog.get_logger(__name__)


def get_anthropic_client() -> anthropic.Anthropic:
    """Initialize the Anthropic client with configured retries"""
    api_key = current_app.config.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY is not set. LLM calls will fail.")
        # We allow initialization without a key so the app doesn't crash on boot,
        # but the actual API call will fail if not mocked.
        api_key = "dummy-key-for-testing"

    return anthropic.Anthropic(api_key=api_key, max_retries=3)
