"""Run an exported Langflow flow JSON as plain Python (no Langflow server/UI needed).

Usage (from the project root):
    python scripts/run_flow_python.py "How many PTO days do I get?"
    python scripts/run_flow_python.py "What is the fix for ORB-1427?" flows/advanced_onboarding_rag.json
"""

import os
import sys

os.environ.setdefault("LANGFLOW_RESTRICT_LOCAL_FILE_ACCESS", "false")

from lfx.load import run_flow_from_json  # noqa: E402

question = sys.argv[1] if len(sys.argv) > 1 else "How many PTO days do I get?"
flow_file = sys.argv[2] if len(sys.argv) > 2 else "flows/onboarding_rag.json"

results = run_flow_from_json(flow=flow_file, input_value=question, disable_logs=True)

print(f"\nQuestion: {question}\n")
for run_output in results:
    for result in run_output.outputs:
        if result is None or not result.results:
            continue
        message = result.results.get("message")
        sender = getattr(message, "sender_name", None) or result.component_display_name
        text = getattr(message, "text", None) or str(result.results)
        print(f"===== {sender} =====\n{text}\n")
