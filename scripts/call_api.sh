#!/usr/bin/env bash
# Usage: ./scripts/call_api.sh "How many PTO days do I get?"
# Needs LANGFLOW_API_KEY (Settings > Langflow API Keys). Reads .env if present.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -f .env ]] && set -a && source .env && set +a

QUESTION="${1:-How many PTO days do I get?}"
URL="${LANGFLOW_URL:-http://127.0.0.1:7860}"
FLOW="${FLOW_ID:-onboarding-rag}"
BODY=$(python3 -c 'import json,sys; print(json.dumps({"input_value": sys.argv[1], "input_type": "chat", "output_type": "chat"}))' "$QUESTION")

curl -sS -X POST "$URL/api/v1/run/$FLOW?stream=false" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${LANGFLOW_API_KEY:-}" \
  -d "$BODY" |
  python3 -c '
import json, sys
body = json.load(sys.stdin)
for run in body.get("outputs", []):
    for out in run.get("outputs", []):
        msg = (out.get("results") or {}).get("message") or {}
        print("===== " + msg.get("sender_name", "output") + " =====")
        print(msg.get("text", "") + "\n")
'
