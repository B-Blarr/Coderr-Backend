"""Finds the knowledge chunks closest to a visitor question."""

from django.conf import settings
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


def keep_relevant(chunks):
    """Drop the chunks below the similarity threshold.

    Filtered here rather than in the query: a WHERE clause next to the
    HNSW index would filter after the index picked its nearest rows.
    """
    threshold = settings.ASSISTANT_MIN_SIMILARITY
    return [chunk for chunk in chunks if 1 - chunk.distance >= threshold]
