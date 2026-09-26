"""Finds the knowledge chunks closest to a visitor question."""

from pgvector.django import CosineDistance

from .embedding_client import embed_query
from .models import KnowledgeChunk

RESULT_COUNT = 5


def search(question, limit=RESULT_COUNT):
    """Return the chunks closest to the question, best match first.

    Every chunk carries a ``distance`` attribute, the cosine distance
    between question and chunk.
    """
    vector = embed_query(question)
    return list(
        KnowledgeChunk.objects
        .defer('embedding')
        .annotate(distance=CosineDistance('embedding', vector))
        .order_by('distance')[:limit]
    )
