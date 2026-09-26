"""Admin configuration for the assistant app."""

from django.contrib import admin

from .models import KnowledgeChunk


@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    """Read-only view of the indexed knowledge base."""

    list_display = ('source', 'position', 'heading')
    list_filter = ('source',)
    search_fields = ('heading', 'content')
    fields = ('source', 'position', 'heading', 'content')
    readonly_fields = fields

    def has_add_permission(self, request):
        """Chunks are only created by the build_index command."""
        return False
