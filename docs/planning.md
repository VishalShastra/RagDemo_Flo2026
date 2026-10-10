# Planning - Decisions, Risks and Rehearsal Checklist

## Decisions

| Topic                  | Decision                                                  | Reason                                                                                                                                    |
| ---------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Platform               | Langflow **1.12.5** (pinned) + `lfx-bundles` 1.1.36       | Visual canvas for teaching, JSON export, REST API and `lfx` runtime in one tool                                                           |
| Install                | `uv` + project `.venv`                                    | No admin rights, same commands on all 3 OSes, `uv` brings its own Python 3.12                                                             |
| LLM                    | `qwen2.5:3b` via Ollama                                   | Best accuracy-to-size for grounded answers; ~1.9 GB                                                                                       |
| Embeddings             | `nomic-embed-text`                                        | 274 MB, strong retrieval quality, CPU-friendly                                                                                            |
| Vector store           | Chroma (local folder)                                     | No server; persists between runs; deduplicates on re-ingest                                                                               |
| Data                   | Fictional "Orbitly Systems" docs + Jira export            | Facts an LLM can't know, so the before/after difference is obvious; safe to share. Real Confluence/URL sources are shown by the presenter |
| Before/after           | One flow, two lanes, same model and persona               | Only the context differs, so the comparison is fair                                                                                       |
| Flow source of truth   | `flows/*.py` → `scripts/export_flows.py` → `flows/*.json` | Reviewable code, reproducible JSON with fixed node IDs (stable tweak keys)                                                                |
| Advanced reranker      | FlashRank (ONNX) instead of sentence-transformers         | ~22 MB model, no PyTorch download, CPU only                                                                                               |
| Advanced hybrid search | Custom component (Chroma MMR + BM25 + RRF)                | Langflow has no built-in local hybrid retriever                                                                                           |

## Risks and mitigations

| Risk                                          | Mitigation                                                                                            |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Slow laptops / slow answers on CPU            | Warm up the models before the session; `qwen2.5:1.5b` fallback; presenter answers projected           |
| Conference Wi-Fi can't handle model downloads | Pre-work sent a week before; USB stick with the Ollama model folder (`~/.ollama/models`) and wheels   |
| Attendees fall behind                         | Import `flows/onboarding_rag.json` or run `scripts/import_flows.py`; checkpoints in build.md          |
| Corporate laptops block scripts/ports         | Langflow Desktop fallback; presenter-led for the rest of the session                                  |
| Small model answers inconsistently            | Temperature 0.1, strict prompt, tested demo questions                                                 |
| Live Confluence/SSO failure                   | Use `sample_data/` (always works); pre-built `chroma_db/` backup                                      |
| Advanced flow latency (4 LLM calls)           | Pre-warmed; screen recording fallback                                                                 |
| Leaking proprietary data                      | Only fictional data in the repo; credentials in Global Variables; `.env` and `chroma_db/` git-ignored |

## Rehearsal checklist

Verified on Linux (2026-10-09): fresh `requirements.txt` install, both flows import and render, REST via `.py`/`.sh`/`.ps1` (PowerShell 7), `run_flow_python.py`, `lfx serve`, advanced A1-A4.

- [ ] `check_prereqs` passes on a clean **Windows** and **macOS** user account (non-admin) — Linux done
- [x] Fresh Langflow: import `flows/onboarding_rag.json`, then Q1-Q5 show a clear before/after difference
- [x] `scripts/call_api.py`, `.sh` and `.ps1` return both answers
- [x] `scripts/run_flow_python.py` gives the same answers as the UI
- [x] `lfx serve flows/advanced_onboarding_rag.json` answers A1
- [ ] Advanced flow: A5 (metadata filter) tried in the UI — A1-A4 done
- [ ] Manual build segment (minutes 8-27) fits in 19 minutes on a timed run
- [ ] Backup screen recording and `chroma_db*` copies ready
