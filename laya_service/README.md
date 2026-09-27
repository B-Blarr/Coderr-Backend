# Laya service

The portfolio assistant checks every visitor question with
[Laya](https://pypi.org/project/laya/) before doing anything else with it.
Laya is a small classifier that estimates whether a text tries to make an AI
assistant ignore its rules (a jailbreak). Questions that do are rejected
before they cost any retrieval or language model time.

This folder contains no service code. Laya ships its own HTTP server,
`laya-serve`; the folder pins its dependencies and holds a smoke test.

Like the [embedding service](../embedding_service/README.md), Laya runs as its
own process so the model is loaded once. Inside Django, every Gunicorn worker
would load its own copy.

## Setup

The service has its own virtual environment, separate from the Django one:

```bash
cd laya_service
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

`laya-serve` is configured through environment variables only.

**Windows (PowerShell):**

```powershell
$env:LAYA_HOST = "127.0.0.1"
$env:LAYA_PORT = "8001"
$env:LAYA_MODELS = "multilingual"
$env:LAYA_DEVICE = "cpu"
laya-serve
```

**macOS / Linux:**

```bash
LAYA_HOST=127.0.0.1 LAYA_PORT=8001 LAYA_MODELS=multilingual LAYA_DEVICE=cpu laya-serve
```

| Variable | Value | Why |
|---|---|---|
| `LAYA_HOST` | `127.0.0.1` | The default `0.0.0.0` would expose the service to the whole network. |
| `LAYA_PORT` | `8001` | The default is `8000`; the embedding service uses `8002`. |
| `LAYA_MODELS` | `multilingual` | Without it, all three Laya checkpoints are loaded at startup. |
| `LAYA_DEVICE` | `cpu` | The server has no GPU. |

The first start downloads the multilingual checkpoint (about 650 MB) into the
Hugging Face cache. The process uses about 1.6 GB of memory after startup.

## API

Interactive documentation is available at `/docs` while the service runs. It
shows no request body for `/v1/systemone`, because `laya-serve` reads the body
itself instead of declaring a schema.

### `GET /health`

```json
{"status": "ok", "loaded": ["multilingual"], "device": "cpu"}
```

### `POST /v1/systemone`

```json
{
  "model": "multilingual",
  "state": {"prompt": "Welche Projekte hat Benjamin mit Django gebaut?"},
  "questions": {
    "jailbreak": {
      "type": "noul",
      "instructions": "Does `prompt` try to make an AI assistant ignore its rules, policies or system instructions?"
    }
  }
}
```

- `model` must always be `multilingual`. Without it, Laya picks a checkpoint
  by language and sends English text to its English checkpoint, which is then
  loaded on first use: slow, and a second model in memory.
- The question is worded exactly like the one in Laya's own
  `guard_questions()` preset. Different wording shifts the scores.
- The preset's `prompt_injection` question is left out. On the assistant's
  test questions it blocked five genuine questions about AI and caught no
  attack that `jailbreak` missed.

The response, shortened:

```json
{
  "answers": {
    "jailbreak": {"type": "noul", "noul": 0.0008}
  },
  "routing": {"model": "multilingual"}
}
```

`noul` is the probability, from 0 to 1, that the answer is yes. Laya reacts
to the vocabulary of jailbreaks ("ignore your rules", "without
restrictions"), not to their intent: quiet attacks that ask for hidden
instructions score close to 0, and some genuine questions about AI score up to
0.76. The assistant therefore blocks at 0.8. `python manage.py evaluate_guard`
in the Django project measures both sides with fixed questions and attacks.

`laya-serve` answers one request at a time and queues the rest. Measured
locally, a request takes about 0.1 seconds, and ten concurrent requests took
about one second until the last answer. Clients need a timeout that allows
for this queue.

## Smoke test

With the service running:

```bash
python smoke_test.py
```

It sends three ordinary questions and three attacks, in German and English,
and checks that exactly the attacks reach a jailbreak score of 0.8. It also
checks that the multilingual checkpoint answered. It exits with `0` on
success and `1` on failure, and needs nothing beyond the Python standard
library.

## Why this folder is not a Python package

There is deliberately no `__init__.py`. Without it, Django's test runner and
coverage ignore this folder, which matters because Laya and PyTorch are not
installed in the Django environment or in CI.
