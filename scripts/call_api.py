"""Call a Langflow flow over its REST API and print every chat output (both RAG lanes).

Usage:
    python scripts/call_api.py "How many PTO days do I get?"
Reads LANGFLOW_URL, LANGFLOW_API_KEY and FLOW_ID from the environment or from .env.
"""

import gzip
import json
import os
import sys
import urllib.request
import uuid
from pathlib import Path


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_env(Path(__file__).resolve().parent.parent / ".env")

base_url = os.environ.get("LANGFLOW_URL", "http://127.0.0.1:7860").rstrip("/")
flow_id = os.environ.get("FLOW_ID", "onboarding-rag")
api_key = os.environ.get("LANGFLOW_API_KEY", "")
question = sys.argv[1] if len(sys.argv) > 1 else "How many PTO days do I get?"

payload = {
    "input_value": question,
    "input_type": "chat",
    "output_type": "chat",
    "session_id": os.environ.get("SESSION_ID", str(uuid.uuid4())),
    # Tweaks override component settings per request, e.g. retrieve more chunks:
    "tweaks": {"VectorStore-Chroma": {"number_of_results": 4}} if flow_id == "onboarding-rag" else {},
}
request = urllib.request.Request(
    f"{base_url}/api/v1/run/{flow_id}?stream=false",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json", "x-api-key": api_key},
    method="POST",
)
with urllib.request.urlopen(request, timeout=600) as response:
    raw = response.read()
    body = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)

print(f"\nQuestion: {question}\n")
for run_output in body.get("outputs", []):
    for output in run_output.get("outputs", []):
        message = (output.get("results") or {}).get("message") or {}
        sender = message.get("sender_name") or output.get("component_display_name", "output")
        print(f"===== {sender} =====\n{message.get('text', '')}\n")
