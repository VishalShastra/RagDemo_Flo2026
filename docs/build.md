# Build Guide and 45-Minute Live Session Runbook

## 1. Requirements (acceptance criteria)

| #   | Requirement                                                                                           | Done when                                                                                             | Delivered by                                                                 |
| --- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| R1  | RAG pipeline showing **loader, splitter, embeddings, retrieval, generation** with local Ollama models | Each stage is its own node on the canvas and can be inspected                                         | `flows/onboarding_rag.json`                                                  |
| R2  | Clear **before vs after RAG** difference                                                              | One question shows two answers: _Without RAG (LLM only)_ and _With RAG (grounded)_                    | Two lanes in the same flow                                                   |
| R3  | Requirements and runbook that can be followed in **45 minutes**                                       | Checkpoints every 4-8 minutes, with a catch-up path                                                   | This file                                                                    |
| R4  | **Setup prerequisites** for Windows, Linux and macOS                                                  | No admin rights needed; checked by a script                                                           | `docs/design.md` §6, `scripts/check_prereqs.*`                               |
| R5  | **Export/import** to other machines                                                                   | The JSON imports into a fresh Langflow and runs unchanged                                             | `flows/*.json`, `scripts/import_flows.py`                                    |
| R6  | Exposed through a **REST API**                                                                        | `curl`/Python/PowerShell clients return both answers                                                  | `scripts/call_api.*`                                                         |
| R7  | Flow **converted to / run as Python**                                                                 | The UI shows the generated code; the same flow runs with no UI                                        | API access pane, `scripts/run_flow_python.py`, `flows/*.py`, `lfx run/serve` |
| R8  | **Advanced RAG** showcase (presenter only)                                                            | Memory, rewriting, multi-query, MMR, BM25 hybrid, reranking, citations and grounding check shown live | `flows/advanced_onboarding_rag.json`                                         |

## 2. Presenter preparation (day before)

1. Complete `docs/design.md` §6 on the presenter laptop, using `requirements-advanced.txt`.
2. `./scripts/check_prereqs.sh` (or `.ps1`) - everything should be `[OK]`.
3. `uv run langflow run --env-file .env`, then `python scripts/import_flows.py --api-key` and paste the key into `.env`.
4. **Warm-up** (loads the models, builds `chroma_db/`, downloads the reranker model):
   ```bash
   python scripts/call_api.py "How many PTO days do I get?"
   FLOW_ID=advanced-onboarding-rag python scripts/call_api.py "What is the fix for ORB-1427?"
   ```
5. Back up `chroma_db/` and `chroma_db_advanced/`, and record a 2-minute screen capture of the advanced flow as a fallback.
6. Share the repo (zip or git URL) with attendees **one week before**, together with design.md §6, so the downloads happen before the session.

Attendees only need `requirements.txt`, the two Ollama models, and `flows/onboarding_rag.json`.

## 3. Runbook (45 minutes)

| Time  | Segment                                                | Presenter does                                                                                                                                                                                                                                                                          | Audience does                                                                               | Checkpoint                                                |
| ----- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| 0-4   | **Intro**                                              | Why RAG: LLMs don't know your company's facts. Show the Orbitly docs in `sample_data/`                                                                                                                                                                                                  | Listen                                                                                      | -                                                         |
| 4-8   | **Environment check**                                  | Run `check_prereqs`; start Langflow                                                                                                                                                                                                                                                     | Same                                                                                        | ✅ `http://127.0.0.1:7860` opens                          |
| 8-12  | **BEFORE: LLM only**                                   | New blank flow: Chat Input → Prompt → Ollama (`qwen2.5:3b`) → Chat Output. Ask Q1                                                                                                                                                                                                       | Build the same 4 nodes                                                                      | ✅ Model answers, but guesses (wrong PTO days, wrong VPN) |
| 12-20 | **Ingestion: Loader → Splitter → Embeddings → Chroma** | Add Directory (`./sample_data`, md) → Split Text (800/150) → Chroma DB (persist `./chroma_db`) + Ollama Embeddings (`nomic-embed-text`). Run the Split Text node and inspect the chunks                                                                                                 | Same                                                                                        | ✅ Split Text output shows ~15 chunks                     |
| 20-27 | **AFTER: Retrieval + Generation**                      | Chat Input → Chroma _Search Query_; Chroma → Parser → Prompt `{context}` + `{question}` → Ollama → Chat Output "With RAG". Ask Q1-Q4                                                                                                                                                    | Same                                                                                        | ✅ Both answers visible; RAG answer cites the source file |
| 27-30 | **Export / Import**                                    | Flow menu → **Export** (leave _Save with my API keys_ unchecked). Then **Upload**/drag `flows/onboarding_rag.json` onto the Projects page                                                                                                                                               | Anyone behind: import `flows/onboarding_rag.json` (or run `python scripts/import_flows.py`) | ✅ Everyone has a working flow                            |
| 30-33 | **REST API**                                           | Settings → Langflow API Keys → create a key. Open **Share → API access** and copy the cURL. Run `scripts/call_api.sh` / `.ps1` / `.py`                                                                                                                                                  | Run one client                                                                              | ✅ JSON response contains both answers                    |
| 33-36 | **Flow → Python**                                      | (a) API access pane → **Python** tab (generated client code). (b) Open a component's **Code** to show it is plain Python. (c) `python scripts/run_flow_python.py "…"` runs the exported JSON with no server. (d) Show `flows/onboarding_rag.py` + `lfx run flows/onboarding_rag.py "…"` | Run (c)                                                                                     | ✅ Same answers from a terminal                           |
| 36-43 | **Advanced RAG showcase** (demo only)                  | Open _Advanced Onboarding RAG_. Walk through the notes left → right. Run A1-A4 and open the debug outputs                                                                                                                                                                               | Watch                                                                                       | -                                                         |
| 43-45 | **Q&A / next steps**                                   | Point to design.md §4 "Concepts to explore next"                                                                                                                                                                                                                                        | Ask                                                                                         | -                                                         |

**If you fall behind:** skip the manual build in 12-27. Import `flows/onboarding_rag.json` and explain the nodes that are already wired. That saves about 10 minutes.

## 4. Demo questions

### Hands-on flow: before vs after

| #   | Question                                                    | Expected "With RAG" fact                                        | Typical "Without RAG" failure            |
| --- | ----------------------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------- |
| Q1  | How many PTO days do I get, and can I carry them over?      | 22 days; up to 5 carried over, expiring 31 March                | Generic "15 days, check with HR"         |
| Q2  | What VPN do I use and which authenticator app is approved?  | OrbitGate; Okta Verify only, no SMS                             | Invents Google Authenticator / "any VPN" |
| Q3  | What is the on-call rotation called and when does it start? | Orbit Watch, 7 days, starting Wednesday 10:00 IST               | Generic on-call explanation              |
| Q4  | Can I deploy to production on Friday?                       | No: Monday-Thursday 10:00-16:00 IST; code freeze 15 Dec - 5 Jan | Usually says "yes, follow your process"  |
| Q5  | What is Recharge Friday?                                    | Last Friday of each month, company off, not counted as PTO      | Made-up wellness program                 |

### Advanced flow (presenter)

| #   | Prompt                                                                    | What it shows                                                                                          |
| --- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| A1  | "What is the fix for ORB-1427?"                                           | **BM25** finds the exact ticket key. Compare the dense and BM25 hits in _Debug: retrieval trace_       |
| A2  | "How many PTO days do employees get?" then "What about contractors?"      | **Memory + query rewriting**: the follow-up is rewritten (see _Debug: queries_)                        |
| A3  | "Podman fails to start on Windows 11, what should I do?"                  | **Multi-query + rerank**: _Debug: rerank trace_ shows positions changing (`#1 (was #3)`)               |
| A4  | "What is the CEO's favourite football club?"                              | **Grounding gate**: the judge fails it and the safe fallback is returned instead of an invented answer |
| A5  | Set _Metadata Filter_ = `jira` on the Hybrid Retriever, then ask A3 again | **Metadata filtering** limits results to the Jira export                                               |

## 5. Command cheat sheet

```bash
# Start Langflow (always from the project root)
uv run langflow run --env-file .env

# Catch-up: import both flows + create an API key
uv run python scripts/import_flows.py --api-key
# After regenerating flows/*.json, overwrite the imported copies
uv run python scripts/import_flows.py --replace

# REST API (endpoint names: onboarding-rag, advanced-onboarding-rag)
uv run python scripts/call_api.py "How many PTO days do I get?"
./scripts/call_api.sh "What VPN do I use?"
.\scripts\call_api.ps1 "What VPN do I use?"                 # Windows

# Raw curl
curl -X POST "http://127.0.0.1:7860/api/v1/run/onboarding-rag?stream=false" \
  -H "Content-Type: application/json" -H "x-api-key: $LANGFLOW_API_KEY" \
  -d '{"input_value": "How many PTO days do I get?", "input_type": "chat", "output_type": "chat",
       "tweaks": {"VectorStore-Chroma": {"number_of_results": 6}}}'

# Flow as Python (no Langflow server)
uv run python scripts/run_flow_python.py "How many PTO days do I get?"
uv run lfx run flows/onboarding_rag.py "How many PTO days do I get?" --format text

# Flow as a standalone microservice (no UI)
LANGFLOW_API_KEY=local-demo-key LANGFLOW_RESTRICT_LOCAL_FILE_ACCESS=false \
  uv run lfx serve flows/advanced_onboarding_rag.json --port 8000
curl -H "x-api-key: local-demo-key" http://127.0.0.1:8000/flows          # get the flow id
curl -X POST http://127.0.0.1:8000/flows/<flow_id>/run -H "x-api-key: local-demo-key" \
  -H "Content-Type: application/json" -d '{"input_value": "What is the fix for ORB-1427?"}'

# After editing flows/*.py, regenerate the importable JSON
uv run python scripts/export_flows.py
```

## 6. Troubleshooting

| Symptom                                                | Fix                                                                                                               |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `Access to local file paths ... is disabled`           | `.env` is missing `LANGFLOW_RESTRICT_LOCAL_FILE_ACCESS=false`, or Langflow was started without `--env-file .env`  |
| `Directory path escapes the allowed root`              | Start Langflow from the project root, or use a path inside it                                                     |
| Ollama node: empty model dropdown / connection refused | Start Ollama (`ollama serve` or the tray app). Check `http://localhost:11434`, then click refresh on the dropdown |
| `model "qwen2.5:3b" not found`                         | `ollama pull qwen2.5:3b`                                                                                          |
| Answers are slow (>60 s)                               | First call loads the model, so warm up. Use `qwen2.5:1.5b` on 8 GB laptops; close other apps                      |
| RAG answer ignores the docs                            | Check the Chroma node output (chunks found?). Delete `chroma_db/` and re-run after changing the embedding model   |
| REST call returns 401/403                              | Create an API key in Settings and send it as `x-api-key`                                                          |
| Port 7860 busy                                         | `uv run langflow run --env-file .env --port 7861` and update `LANGFLOW_URL`                                       |
| Imported flow shows "outdated component"               | Click **Update** on the node. The flows were built with Langflow 1.12.5                                           |
| Advanced flow: `No module named rank_bm25 / flashrank` | `uv pip install -r requirements-advanced.txt`                                                                     |
