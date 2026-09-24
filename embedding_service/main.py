"""HTTP service that turns texts into multilingual-e5-base embeddings."""

from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, StringConstraints
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-base"
MAX_TEXTS_PER_REQUEST = 64

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model once at startup instead of once per request."""
    ml_models["embedder"] = SentenceTransformer(MODEL_NAME, device="cpu")
    yield
    ml_models.clear()


app = FastAPI(title="Embedding service", lifespan=lifespan)

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class EmbedRequest(BaseModel):
    """Texts to embed, marked as search queries or knowledge passages."""

    kind: Literal["query", "passage"]
    texts: Annotated[
        list[Text], Field(min_length=1, max_length=MAX_TEXTS_PER_REQUEST)
    ]


class EmbedResponse(BaseModel):
    """One normalized vector per input text, in input order."""

    model: str
    dimensions: int
    vectors: list[list[float]]


@app.get("/health")
def health():
    """Report readiness. Uvicorn only answers once the model is loaded."""
    return {"status": "ok", "model": MODEL_NAME}


def _reject_truncated(embedder, texts):
    """Refuse texts the model would silently cut off at its token limit."""
    token_counts = [
        len(ids) for ids in embedder.tokenizer(texts)["input_ids"]
    ]
    too_long = [
        index for index, count in enumerate(token_counts)
        if count > embedder.max_seq_length
    ]
    if too_long:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Text exceeds the model's token limit.",
                "limit": embedder.max_seq_length,
                "indexes": too_long,
            },
        )


@app.post("/embed")
def embed(request: EmbedRequest) -> EmbedResponse:
    """Return one normalized embedding per text."""
    embedder = ml_models["embedder"]
    # e5 was trained with these prefixes. Without them it still returns
    # vectors, but retrieval quality drops without any error.
    texts = [f"{request.kind}: {text}" for text in request.texts]
    _reject_truncated(embedder, texts)
    vectors = embedder.encode(texts, normalize_embeddings=True)
    return EmbedResponse(
        model=MODEL_NAME,
        dimensions=vectors.shape[1],
        vectors=vectors.tolist(),
    )
