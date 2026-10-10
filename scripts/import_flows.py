"""Import the flows in flows/*.json into a running local Langflow (catch-up helper for attendees).

Usage:  python scripts/import_flows.py            # imports all exported flows
        python scripts/import_flows.py --api-key  # also creates and prints a Langflow API key
        python scripts/import_flows.py --replace  # deletes previously imported copies first
Works with the default single-user mode (LANGFLOW_AUTO_LOGIN=true). Otherwise import via the UI.
"""

import gzip
import json
import os
import sys
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get("LANGFLOW_URL", "http://127.0.0.1:7860").rstrip("/")


def call(method: str, path: str, token: str | None = None, body: bytes | None = None, ctype: str = "application/json"):
    headers = {"Content-Type": ctype}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        if raw := resp.read():
            return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
        return None


token = call("GET", "/api/v1/auto_login")["access_token"]
existing = {
    f.get("endpoint_name"): f["id"] for f in call("GET", "/api/v1/flows/?get_all=true&header_flows=true", token)
}

for flow_file in sorted((ROOT / "flows").glob("*.json")):
    flow = json.loads(flow_file.read_text(encoding="utf-8"))
    if flow.get("endpoint_name") in existing:
        if "--replace" not in sys.argv:
            print(f"skip   {flow['name']} (already imported; use --replace)")
            continue
        call("DELETE", f"/api/v1/flows/{existing[flow['endpoint_name']]}", token)
    boundary = uuid.uuid4().hex
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{flow_file.name}"\r\n'
        f"Content-Type: application/json\r\n\r\n{json.dumps(flow)}\r\n--{boundary}--\r\n"
    ).encode()
    created = call("POST", "/api/v1/flows/upload/", token, body, f"multipart/form-data; boundary={boundary}")
    print(f"import {created[0]['name']} -> {BASE}/flow/{created[0]['id']}")

if "--api-key" in sys.argv:
    key = call("POST", "/api/v1/api_key/", token, json.dumps({"name": f"demo-{uuid.uuid4().hex[:6]}"}).encode())
    print(f"\nLANGFLOW_API_KEY={key['api_key']}  (put this in .env)")
