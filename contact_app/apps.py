"""App configuration for the contact app."""

from django.apps import AppConfig


class ContactAppConfig(AppConfig):
    """Default configuration for the contact app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contact_app'
    verbose_name = "Kontakt"
