#!/usr/bin/env bash
# Pre-session check for Linux/macOS. Usage: ./scripts/check_prereqs.sh
cd "$(dirname "$0")/.."
LLM_MODEL="${LLM_MODEL:-qwen2.5:3b}"
EMBED_MODEL="${EMBED_MODEL:-nomic-embed-text}"
fail=0
ok()   { printf "  [OK]   %s\n" "$1"; }
bad()  { printf "  [FAIL] %s\n         -> %s\n" "$1" "$2"; fail=1; }

echo "Checking RAG demo prerequisites..."
command -v uv >/dev/null && ok "uv $(uv --version | cut -d' ' -f2)" \
  || bad "uv not found" "curl -LsSf https://astral.sh/uv/install.sh | sh  (then open a new terminal)"

if [[ -x .venv/bin/python ]]; then
  ok "virtual env .venv ($(.venv/bin/python --version))"
  v=$(.venv/bin/python -c "import importlib.metadata as m; print(m.version('langflow'))" 2>/dev/null) \
    && ok "langflow $v" || bad "langflow not installed in .venv" "uv pip install -r requirements.txt"
else
  bad ".venv missing" "uv venv --python 3.12 && uv pip install -r requirements.txt"
fi

command -v ollama >/dev/null && ok "ollama binary" \
  || bad "ollama not found" "see docs/design.md > Prerequisites for a no-admin install"
if curl -fsS http://localhost:11434/api/tags >/tmp/ollama_tags.json 2>/dev/null; then
  ok "ollama server on :11434"
  for m in "$LLM_MODEL" "$EMBED_MODEL"; do
    grep -q "\"${m%%:*}" /tmp/ollama_tags.json && ok "model $m" || bad "model $m missing" "ollama pull $m"
  done
else
  bad "ollama server not reachable on :11434" "run: ollama serve"
fi

if curl -fsS http://127.0.0.1:7860/health >/dev/null 2>&1; then
  ok "Langflow already running on :7860"
elif (echo >/dev/tcp/127.0.0.1/7860) 2>/dev/null; then
  bad "port 7860 is used by another app" "langflow run --port 7861 --env-file .env"
else
  ok "port 7860 free"
fi
[[ -f .env ]] && ok ".env present" || bad ".env missing" "cp .env.example .env"

[[ $fail -eq 0 ]] && echo "All good - start with: uv run langflow run --env-file .env" || echo "Fix the items above."
exit $fail
