"""Management command that rebuilds the assistant's knowledge index."""

from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from assistant_app.embedding_client import (
    EmbeddingServiceError,
    embed_passages,
)
from assistant_app.knowledge_base import KnowledgeBaseError, read_sections
from assistant_app.models import KnowledgeChunk


class Command(BaseCommand):
    """Embeds every knowledge section and replaces the stored index."""

    help = "Rebuild the assistant's knowledge index from knowledge/*.md."

    def handle(self, *args, **options):
        """Build the new index completely before touching the old one."""
        app_path = Path(apps.get_app_config('assistant_app').path)
        try:
            sections = read_sections(app_path / 'knowledge')
            vectors = embed_passages([s.passage for s in sections])
        except (KnowledgeBaseError, EmbeddingServiceError) as error:
            raise CommandError(error) from error
        self._replace_index(sections, vectors)
        files = len({section.source for section in sections})
        self.stdout.write(self.style.SUCCESS(
            f"Indexed {len(sections)} sections from {files} files."
        ))

    def _replace_index(self, sections, vectors):
        """Swap old for new chunks in one transaction."""
        chunks = [
            KnowledgeChunk(
                source=section.source,
                position=section.position,
                heading=section.heading,
                content=section.content,
                embedding=vector,
            )
            for section, vector in zip(sections, vectors, strict=True)
        ]
        with transaction.atomic():
            KnowledgeChunk.objects.all().delete()
            KnowledgeChunk.objects.bulk_create(chunks)
