# HarborPay project onboarding RAG flow

This sample Langflow pipeline answers questions about the 20 fictional payment-gateway onboarding documents in [sample_data](../sample_data). It supports QA, developer, business analyst (BA), and manager questions without needing a real payment system or credentials.

Import [harborpay_onboarding_rag.json](../flows/harborpay_onboarding_rag.json). The reproducible Python graph is [harborpay_onboarding_rag.py](../flows/harborpay_onboarding_rag.py). The older flows remain unchanged.

## Pipeline

```text
Directory -> Split Text -> Chroma ingest
Ollama Embeddings --------> Chroma embedding
Chat Input --------------> Chroma search query
Chroma search -> Parser -> Prompt Template -> Ollama -> Answer + Retrieved Sources -> Chat Output
Chat Input -------------> Prompt question
Parser -----------------> Answer + Retrieved Sources context
Parser -----------------> Retrieved Evidence Chat Output
```

The same Chroma node ingests and searches for this teaching example. Conceptually, document indexing and question-time retrieval are separate stages; this is not a production ingestion scheduler.

The knowledge node is a small custom [Project Chroma DB](../components/project_chroma.py) component extending the standard Chroma node. It uses deterministic IDs derived from source path and passage text, so repeated questions do not add duplicate copies of unchanged passages. Its code is included in the JSON export; importing the flow does not require copying the component file. It still uses the base Chroma/Ollama dependencies.

[Answer + Retrieved Sources](../components/source_answer.py) preserves the model text and appends a deduplicated list of filenames from the retrieved context. This keeps sources visible when a small model omits inline citations. The list is labeled as retrieved evidence, not verified support for every generated claim; inspect the separate evidence output. Empty model output or malformed nonempty source context raises an explicit error.

## Import and configure

1. Complete the [base setup](../README.md#quick-start): Python 3.12, base requirements, Ollama, `qwen2.5:3b`, and `nomic-embed-text`.
2. Start Langflow from the repository root, using the local `.env` settings. Do not expose the unrestricted local-file-access demo to untrusted networks.
3. Upload the HarborPay JSON on the Projects page. Importing JSON does not copy the source documents or vector database to another machine.
4. Check Directory's path: `./sample_data`, or an absolute local path to these documents. Directory reports loading errors rather than hiding them.
5. Check both Ollama URLs and model selections. For a remote/container setup, `localhost` must refer to the actual model host; change the nodes deliberately.
6. Check Chroma's writable persistence directory and collection below.
7. Open Playground and submit a role-specific question. Inspect **HarborPay onboarding assistant** and **Retrieved project evidence**; depending on the UI, select the output you want to run/view.

The evidence output is not stored in chat history. It displays source-labeled retrieved passages, not a separately generated interpretation. The assistant does not use conversational memory: include your role and full question each time.

## Default settings

| Setting | Value |
|---|---|
| Documents | `./sample_data`, Markdown only |
| Chunk size / overlap | 1200 / 200 characters |
| Embedding model | `nomic-embed-text:latest` |
| Retrieval | Similarity, six results |
| Chroma collection | `harborpay_project_onboarding` |
| Chroma persistence | `./chroma_db_harborpay` |
| Chat model | `qwen2.5:3b`, temperature 0 |
| Model context window | 8192 tokens requested |
| API endpoint | `harborpay-onboarding-rag` |

These are starter settings, not measured optimal thresholds. The paragraph splitter targets 1200 characters but can produce larger chunks for long paragraphs/tables. Larger chunks aim to keep onboarding conditions together; six results provide more evidence than the older basic flow. The requested context window must be supported by the selected model and machine. Inspect retrieval and evaluate answers before tuning.

## Separate index and environment overrides

The HarborPay collection/directory are separate from `chroma_db` and `chroma_db_advanced`. The original `CHROMA_DIR` environment variable deliberately does not redirect this flow into an older index.

When running/exporting the Python graph, supported variables are `DOCS_PATH`, `OLLAMA_BASE_URL`, `LLM_MODEL`, `EMBED_MODEL`, and `HARBORPAY_CHROMA_DIR`. The importable JSON contains the values captured when exported; set its node fields directly or regenerate after changing environment variables.

After source edits, removed passages can remain in a persisted index. Use a new empty HarborPay persistence directory for a corpus version, preserving existing stores. Changing the embedding model also requires rebuilding into a fresh store; do not mix vector spaces. Do not delete another flow's database.

For a separate corpus version in Windows PowerShell:

```powershell
$env:HARBORPAY_CHROMA_DIR = ".\chroma_db_harborpay\corpus-v2"
.\.venv\Scripts\python.exe scripts\export_flows.py --flow harborpay_onboarding_rag
```

Then reimport the new JSON as a separate flow or update the existing node manually. Generated databases stay inside the ignored HarborPay directory. The export script does not run the model or verify document contents.

## Questions and expected evidence

| Role | Question | Source to inspect |
|---|---|---|
| QA | As a QA engineer, what is my first task and who reviews it? | [QA guide](../sample_data/13_qa_strategy_test_data_and_scenarios.md) and role ownership |
| Developer | What happens if an idempotency key is reused with a changed amount? | [Data/idempotency guide](../sample_data/10_data_model_and_idempotency.md): conflict, no second operation |
| BA | Who approves payment business rules? | [Ownership guide](../sample_data/02_team_roles_and_ownership.md): Product Owner, Finance review |
| Manager | Which signoffs are needed before a release go/no-go? | [Manager guide](../sample_data/15_manager_delivery_and_release_governance.md): QA, business, operational signoffs; delivery decision record |
| Shared | With 25000 paise captured, 5000 refunded and 7000 pending, how much remains refundable? | [Business rules](../sample_data/04_payment_terms_and_business_rules.md): 13000 paise, pending reservations count |
| Unsupported | What is the real production webhook signing secret? | No secret is supplied; expect explicit abstention, never credentials |

More questions are in the [exercise guide](../sample_data/20_faq_glossary_and_onboarding_exercises.md). Source references and abstention are prompt instructions, not guaranteed output or access enforcement. Role-aware wording does not implement document-level authorization.

## Run and regenerate

From the repository root in Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\export_flows.py --flow harborpay_onboarding_rag
.\.venv\Scripts\python.exe scripts\run_flow_python.py "Who approves payment business rules?" flows\harborpay_onboarding_rag.json
```

The generic import helper automatically discovers the new JSON. It imports all available exports; `--replace` deletes existing imported copies, so use manual upload for a non-destructive single-flow import.

Existing REST clients can call the new endpoint:

```powershell
$env:FLOW_ID = "harborpay-onboarding-rag"
.\scripts\call_api.ps1 "Which signoffs are needed before release?"
```

Configure your own Langflow API key through the existing local setup; no credentials are part of this sample.

## Verify a live run

Confirm the loader reads the intended 20 documents, chunks retain `file_path`, Chroma returns relevant passages, and both outputs are connected. Check retrieved source text before checking the generated answer's units, conditions, owners, and citations.

If evidence is missing, inspect loading, paths, embeddings, and retrieval rather than adding unsupported facts to the prompt. If generation fails, show its error; an evidence-only run is not proof that the answer model works. The sample does not guarantee absence of hallucinations or implement a financial application.

## Validation performed

Seven automated tests cover graph connections, export/Python parity, prompt scope, separate storage, repeated-ingestion deduplication, and source-footer/error behavior. Run them with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_harborpay_flow.py -v
```

The exported JSON was also executed with local `nomic-embed-text:latest` and `llama3.2:latest`, using a separate test index. Six checks passed: a QA task/reviewer question, developer idempotency, BA approvals, manager signoffs, refund arithmetic, and unsupported-secret abstention. Repeated runs returned six distinct passages rather than duplicate copies.

The default `qwen2.5:3b` was not installed on the validation machine. Install it as described in the base setup, or choose an available model such as `llama3.2:latest` in the Ollama node. Langflow browser import was not exercised; validation used the actual JSON graph runner. Model quality can vary, and the observed cases do not establish correctness for every onboarding question.
