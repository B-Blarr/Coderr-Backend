#!/usr/bin/env bash
# Sends one request to each model service of the portfolio assistant.
# After hours without a request, the first one took about ten seconds
# (measured on 2026-09-29), twice as long as the Django clients wait.
# Run by assistant-warmup.timer every ten minutes and whenever one of the
# services starts, see DEPLOYMENT.md 5.7.
set -euo pipefail

# Right after a start the model is still loading and the port is closed.
# After a long pause, loading took more than a minute on 2026-09-29.
# The waiting stays quiet, only a service that never comes up is logged.
wait_until_up() {
    local url="$1"
    curl -fs -o /dev/null -m 5 \
        --retry 90 --retry-delay 2 --retry-max-time 180 --retry-connrefused \
        "$url/health" \
        || { echo "$url did not come up within three minutes" >&2; return 1; }
}

# Nobody waits for this run, so a slow first inference is fine.
post_json() {
    local url="$1" body="$2"
    curl -fsS -o /dev/null -m 60 \
        -X POST -H 'Content-Type: application/json' -d "$body" "$url"
}

# A question of its own instead of the real guard question, so that new
# wording in laya_client.py does not have to be copied here.
wait_until_up http://127.0.0.1:8001
post_json http://127.0.0.1:8001/v1/systemone \
    '{"model":"multilingual","state":{"prompt":"warm"},"questions":{"warmup":{"type":"noul","instructions":"Is `prompt` a question?"}}}'
wait_until_up http://127.0.0.1:8002
post_json http://127.0.0.1:8002/embed '{"kind":"query","texts":["warm"]}'
