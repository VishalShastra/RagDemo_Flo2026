# Onboarding RAG Demo

A local, GitHub-shareable onboarding assistant built with Langflow, Ollama, and Chroma. Use it to see the same question answered by an LLM with no company context and by a grounded RAG flow with citations to fictional Orbitly Systems documents.

The hands-on flow makes each stage visible: document loading, text splitting, embeddings, vector storage and retrieval, prompting, and generation. The project also demonstrates flow import/export, REST calls, and running a flow from Python without the Langflow UI.

## Flows

- **Onboarding RAG - Before vs After** (`flows/onboarding_rag.json`): the attendee flow. It returns both an LLM-only answer and a document-grounded answer.
- **Advanced Onboarding RAG** (`flows/advanced_onboarding_rag.json`): a presenter showcase with conversational memory, query rewriting and expansion, dense and BM25 hybrid retrieval, reranking, citations, and a grounding check. Install `requirements-advanced.txt` to use it; these extra dependencies are not needed for the hands-on flow.

The included documents are fictional training data in `sample_data/`. Replace them only with content you are authorized to use.

## Quick Start

The full no-admin installation instructions for Windows, macOS, and Linux are in [docs/design.md](docs/design.md#6-prerequisites-no-admin-rights-needed). They cover installing `uv` and Ollama, model downloads, and platform-specific setup. For a ready-to-run demo, use Python 3.12 and the base requirements below.

1. Install and start [Ollama](https://ollama.com/), then download the default models:

   ```bash
   ollama pull qwen2.5:3b
   ollama pull nomic-embed-text
   ```

2. From the repository root, create the environment and install dependencies:

   ```bash
   uv venv --python 3.12
   uv pip install -r requirements.txt
   cp .env.example .env
   ```

   On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

3. Check prerequisites and start Langflow:

   ```bash
   ./scripts/check_prereqs.sh
   uv run langflow run --env-file .env
   ```

   On Windows PowerShell, run `powershell -ExecutionPolicy Bypass -File .\scripts\check_prereqs.ps1` for the check. Open <http://127.0.0.1:7860>.

4. Import `flows/onboarding_rag.json` from Langflow's Projects page, then open the flow in the Playground and ask a question. For the API and Python-only routes, see below.

The hands-on flow needs Ollama running locally and the models above. The advanced flow additionally needs:

```bash
uv pip install -r requirements-advanced.txt
```

## Try It

Questions with answers grounded in the sample documents include:

- How many PTO days do I get, and can I carry them over?
- What VPN do I use and which authenticator app is approved?
- What is the on-call rotation called and when does it start?
- Can I deploy to production on Friday?

### REST API

Create a Langflow API key in Settings, then call the named endpoint. The client scripts support Python, Bash, and PowerShell:

```bash
uv run python scripts/call_api.py "How many PTO days do I get?"
./scripts/call_api.sh "What VPN do I use?"
```

```powershell
.\scripts\call_api.ps1 "What VPN do I use?"
```

The basic and advanced endpoint names are `onboarding-rag` and `advanced-onboarding-rag`. For a raw `curl` example and standalone `lfx serve`, see [docs/build.md](docs/build.md#5-command-cheat-sheet).

### Run Without the Langflow UI

Run the exported JSON flow directly as Python:

```bash
uv run python scripts/run_flow_python.py "How many PTO days do I get?"
```

The Python-defined flow can also be run with `lfx`:

```bash
uv run lfx run flows/onboarding_rag.py "How many PTO days do I get?" --format text
```

## Repository Guide

| Path                        | Purpose                                                                            |
| --------------------------- | ---------------------------------------------------------------------------------- |
| `flows/`                    | Importable JSON exports and Python flow definitions                                |
| `components/`               | Custom hybrid retrieval, reranking, and grounding components for the advanced flow |
| `sample_data/`              | Fictional onboarding documents and a simulated Jira export                         |
| `scripts/`                  | Prerequisite checks, flow import/export, REST clients, and Python runner           |
| `requirements.txt`          | Base Langflow dependencies                                                         |
| `requirements-advanced.txt` | Additional presenter-only retrieval and reranking dependencies                     |
| `docs/design.md`            | Architecture, model choices, and OS-specific setup                                 |
| `docs/build.md`             | 45-minute session runbook, demo questions, command reference, and troubleshooting  |
| `docs/planning.md`          | Project plan and progress                                                          |

To regenerate the JSON files after editing a Python flow:

```bash
uv run python scripts/export_flows.py
```

## Security and Local Data

This demo is configured for local use. `.env`, virtual environments, Chroma databases, and the FlashRank cache are excluded by `.gitignore`; do not commit API keys, credentials, proprietary documents, or generated vector stores. `LANGFLOW_RESTRICT_LOCAL_FILE_ACCESS=false` is used for local access to the sample files. Do not expose a Langflow server with this setting on a shared or untrusted network.

## Validation Notes

The project has been exercised on Linux, including the basic flow and API/Python paths. PowerShell scripts were checked in a Docker PowerShell environment. Real Windows and macOS non-admin setup and the timed 45-minute rehearsal have not yet been verified.
