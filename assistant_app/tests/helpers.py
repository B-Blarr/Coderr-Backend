"""Helpers shared by the assistant tests."""

from assistant_app.models import KnowledgeChunk


def unit_vector(axis):
    """Return a 768-dimensional vector that points along one axis."""
    vector = [0.0] * 768
    vector[axis] = 1.0
    return vector


def mixed_vector(weights):
    """Return a unit vector split across axes, e.g. {3: 0.8, 4: 0.6}."""
    vector = [0.0] * 768
    for axis, weight in weights.items():
        vector[axis] = weight
    return vector


def ranked(*headings):
    """Return unsaved chunks in the given order, best match first."""
    chunks = []
    for rank, heading in enumerate(headings, start=1):
        chunk = KnowledgeChunk(heading=heading)
        chunk.distance = rank / 10
        chunks.append(chunk)
    return chunks
