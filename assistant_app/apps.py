"""App configuration for the assistant app."""

from django.apps import AppConfig
from django.core.checks import register


class AssistantAppConfig(AppConfig):
    """Default configuration for the assistant app."""

    name = 'assistant_app'
    verbose_name = "Assistent"

    def ready(self):
        """Register the checks for the language model settings."""
        from .checks import check_llm_settings
        register(check_llm_settings)
