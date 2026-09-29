#!/usr/bin/env bash
# Sends one request to each model service of the portfolio assistant.
# After hours without a request, the first one took about ten seconds
# (measured on 2026-09-29), twice as long as the Django clients wait.
# Run by assistant-warmup.timer every ten minutes and whenever one of the
# services starts, see DEPLOYMENT.md 5.7.
set -euo pipefail

# Nobody waits for this run, so a slow first inference is fine. Right
# after a start the model is still loading and the port is closed,
# hence the retries.
post_json() {
    local url="$1" body="$2"
    curl -fsS -o /dev/null -m 60 \
        --retry 30 --retry-delay 2 --retry-max-time 120 --retry-connrefused \
        -X POST -H 'Content-Type: application/json' -d "$body" "$url"
}

# A question of its own instead of the real guard question, so that new
# wording in laya_client.py does not have to be copied here.
post_json http://127.0.0.1:8001/v1/systemone \
    '{"model":"multilingual","state":{"prompt":"warm"},"questions":{"warmup":{"type":"noul","instructions":"Is `prompt` a question?"}}}'
post_json http://127.0.0.1:8002/embed '{"kind":"query","texts":["warm"]}'
