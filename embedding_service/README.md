# Embedding service

A small FastAPI service that turns texts into 768-dimensional vectors with
[`intfloat/multilingual-e5-base`](https://huggingface.co/intfloat/multilingual-e5-base).
The portfolio assistant uses it to index the knowledge base and to embed
visitor questions.

It runs as its own process so the model is loaded once. Inside Django, every
Gunicorn worker would load its own copy.

## Setup

The service has its own virtual environment, separate from the Django one:

```bash
cd embedding_service
python -m venv .venv
```

Activate it. **Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Then install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` pulls the CPU-only PyTorch build from the PyTorch package
index. The default Linux wheel on PyPI would add several gigabytes of CUDA
libraries.

## Running

```bash
uvicorn main:app --host 127.0.0.1 --port 8002
```

The first start downloads the model (about 1.1 GB) into the Hugging Face
cache. Uvicorn only accepts connections once the model is loaded. The process
uses about 1.8 GB of memory after the first request.

## API

Interactive documentation is available at `/docs` while the service runs.

### `GET /health`

```json
{"status": "ok", "model": "intfloat/multilingual-e5-base"}
```

### `POST /embed`

```json
{"kind": "query", "texts": ["Wie deployt Benjamin seine Projekte?"]}
```

- `kind` is `query` for search questions and `passage` for knowledge base
  sections. The service adds the prefix e5 was trained with. Without it the
  model still returns vectors, but retrieval quality drops without any error.
- `texts` holds 1 to 64 non-blank strings.

The response contains one vector per text, in input order:

```json
{"model": "intfloat/multilingual-e5-base", "dimensions": 768, "vectors": [[0.026, 0.063, ...]]}
```

Vectors are normalized to length 1, so their dot product is the cosine
similarity. e5 scores cluster between roughly 0.7 and 1.0 even for unrelated
texts. Only their order is meaningful, not their absolute value.

Invalid input returns `422`. So does any text longer than the model's limit
of 512 tokens, which the model would otherwise cut off silently.
`detail.indexes` lists the positions of the affected texts.

## Smoke test

With the service running:

```bash
python smoke_test.py
```

It checks the vector size and that related passages, German and English,
score higher than an unrelated one. It exits with `0` on success and `1` on
failure, and needs nothing beyond the Python standard library.

## Why this folder is not a Python package

There is deliberately no `__init__.py`. Without it, Django's test runner and
coverage ignore this folder, which matters because FastAPI and PyTorch are not
installed in the Django environment or in CI.
