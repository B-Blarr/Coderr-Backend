"""System checks for the assistant app."""

from django.conf import settings
from django.core import checks

from .llm_client import PROFILES


def check_llm_settings(app_configs, **kwargs):
    """Report LLM settings that would make answers fail."""
    messages = []
    if settings.ASSISTANT_LLM_PROFILE not in PROFILES:
        messages.append(checks.Error(
            f"Unknown ASSISTANT_LLM_PROFILE "
            f"{settings.ASSISTANT_LLM_PROFILE!r}.",
            hint=f"Use one of: {', '.join(PROFILES)}.",
            id='assistant_app.E001'))
    if settings.ASSISTANT_ENABLED and not settings.ANTHROPIC_API_KEY:
        messages.append(checks.Warning(
            "ASSISTANT_ENABLED is set, but ANTHROPIC_API_KEY is missing.",
            hint="Every answer fails with 503 until the key is set.",
            id='assistant_app.W001'))
    return messages
