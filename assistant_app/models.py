"""Database models for the assistant app."""

from django.db import models
from pgvector.django import HnswIndex, VectorField


class KnowledgeChunk(models.Model):
    """One section of the knowledge base together with its embedding.

    The table is rebuilt from the Markdown files by ``build_index`` and
    is never edited by hand.
    """

    source = models.CharField(max_length=100)
    position = models.PositiveSmallIntegerField()
    heading = models.CharField(max_length=200)
    content = models.TextField()
    embedding = VectorField(dimensions=768)

    class Meta:
        ordering = ['source', 'position']
        verbose_name = "Wissensabschnitt"
        verbose_name_plural = "Wissensabschnitte"
        indexes = [
            HnswIndex(
                name='chunk_embedding_hnsw',
                fields=['embedding'],
                opclasses=['vector_cosine_ops'],
            ),
        ]

    def __str__(self):
        """Return source and heading as the chunk label."""
        return f"{self.source}: {self.heading}"
