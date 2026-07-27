"""Admin configuration for the contact app."""

from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Read-only view of received contact messages."""

    list_display = ('created_at', 'name', 'email', 'mail_sent')
    list_filter = ('mail_sent', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = (
        'name', 'email', 'message', 'created_at', 'ip_address', 'mail_sent',
    )

    def has_add_permission(self, request):
        """Messages are only created through the API."""
        return False
