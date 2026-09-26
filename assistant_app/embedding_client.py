"""Client for the local embedding service in embedding_service/."""

import httpx
from django.conf import settings

MAX_TEXTS_PER_REQUEST = 64
QUERY_TIMEOUT = 5
PASSAGE_TIMEOUT = 120


class EmbeddingServiceError(Exception):
    """The embedding service is unreachable or rejected the request."""


def embed_query(text):
    """Return the vector for one visitor question."""
    return _post('query', [text], QUERY_TIMEOUT)[0]


def embed_passages(texts):
    """Return one vector per knowledge passage, in input order.

    The service accepts at most 64 texts per request, so longer lists
    are sent in batches.
    """
    vectors = []
    for start in range(0, len(texts), MAX_TEXTS_PER_REQUEST):
        batch = texts[start:start + MAX_TEXTS_PER_REQUEST]
        vectors.extend(_post('passage', batch, PASSAGE_TIMEOUT))
    return vectors


def _post(kind, texts, timeout):
    """Send one request to /embed and return its vectors."""
    try:
        response = httpx.post(
            f"{settings.EMBEDDING_SERVICE_URL}/embed",
            json={'kind': kind, 'texts': texts},
            timeout=timeout,
        )
    except httpx.HTTPError as error:
        raise EmbeddingServiceError(
            f"Embedding service not reachable: {error!r}"
        ) from error
    if response.status_code != 200:
        raise EmbeddingServiceError(
            f"Embedding service answered {response.status_code}: "
            f"{response.text}"
        )
    return response.json()['vectors']
