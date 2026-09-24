"""Smoke test for a running embedding service.

Checks the vector size and that related passages, in German and in English,
score higher than an unrelated one. Uses only the standard library, so it
runs with any Python 3, including on the server after a deploy.
"""

import json
import sys
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8002"
EXPECTED_DIMENSIONS = 768

QUERY = "Wie bringt Benjamin seine Projekte auf den Server?"
PASSAGES = {
    "related, German": (
        "Das Deployment läuft automatisch über GitHub Actions "
        "auf einen eigenen VPS."
    ),
    "related, English": (
        "Deployment runs automatically through GitHub Actions "
        "to a private VPS."
    ),
    "unrelated": (
        "Der Pokedex zeigt Pokémon mit ihren Typen und Werten "
        "in einer Kartenansicht."
    ),
}


def embed(kind, texts):
    """Send texts to the service and return their vectors."""
    body = json.dumps({"kind": kind, "texts": texts}).encode("utf-8")
    request = Request(
        f"{BASE_URL}/embed",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)["vectors"]


def cosine(a, b):
    """Cosine similarity of two normalized vectors, their dot product."""
    return sum(x * y for x, y in zip(a, b))


def main():
    """Print the similarity scores and return 1 if a check fails."""
    [query] = embed("query", [QUERY])
    vectors = embed("passage", list(PASSAGES.values()))
    scores = {
        label: cosine(query, vector)
        for label, vector in zip(PASSAGES, vectors)
    }

    for label, score in scores.items():
        print(f"{score:.4f}  {label}")

    failures = []
    if len(query) != EXPECTED_DIMENSIONS:
        failures.append(f"expected {EXPECTED_DIMENSIONS} dimensions")
    for label in ("related, German", "related, English"):
        if scores[label] <= scores["unrelated"]:
            failures.append(f"'{label}' does not beat 'unrelated'")

    for failure in failures:
        print(f"FAIL: {failure}")
    print("FAILED" if failures else "OK")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
