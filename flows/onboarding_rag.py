"""Onboarding RAG (hands-on flow): ingestion lane + side-by-side "Without RAG" vs "With RAG" lanes.

Run without the UI:   lfx run flows/onboarding_rag.py "How many PTO days do I get?"
Serve as REST API:    lfx serve flows/onboarding_rag.py
"""

import os
from textwrap import dedent

from lfx.components.chroma import ChromaVectorStoreComponent
from lfx.components.files_and_knowledge.directory import DirectoryComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.components.models_and_agents import PromptComponent
from lfx.components.ollama import ChatOllamaComponent, OllamaEmbeddingsComponent
from lfx.components.processing import ParserComponent
from lfx.components.processing.split_text import SplitTextComponent
from lfx.graph import Graph

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text:latest")
DOCS_PATH = os.getenv("DOCS_PATH", "./sample_data")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
COLLECTION = "onboarding_docs"

SYSTEM_PERSONA = "You are the onboarding assistant for Orbitly Systems. Answer the new joiner's question."

NO_RAG_TEMPLATE = dedent(
    """\
    {persona}

    Question: {question}
    Answer:"""
)

RAG_TEMPLATE = dedent(
    """\
    {persona}
    Use ONLY the context below. If the answer is not in the context, say "I don't know based on the onboarding docs."
    Mention the source file name for each fact.

    Context:
    {context}

    Question: {question}
    Answer:"""
)


def _llm(node_id: str) -> ChatOllamaComponent:
    llm = ChatOllamaComponent(_id=node_id)
    llm.set(base_url=OLLAMA_URL, model_name=LLM_MODEL, temperature=0.1)
    return llm


def build_graph() -> Graph:
    chat_input = ChatInput(_id="Question-ChatInput")

    # 1. Ingestion lane: Loader -> Splitter -> Embeddings -> Vector store
    loader = DirectoryComponent(_id="Loader-Directory")
    loader.set(path=DOCS_PATH, types=["md", "txt"])

    splitter = SplitTextComponent(_id="Splitter-SplitText")
    splitter.set(data_inputs=loader.as_dataframe, chunk_size=800, chunk_overlap=150, separator="\n\n")

    # 3a. "Before" lane: plain LLM, no retrieval
    no_rag_prompt = PromptComponent(_id="NoRAG-Prompt")
    no_rag_prompt.set(template=NO_RAG_TEMPLATE, persona=SYSTEM_PERSONA, question=chat_input.message_response)
    no_rag_llm = _llm("NoRAG-Ollama")
    no_rag_llm.set(input_value=no_rag_prompt.build_prompt)
    no_rag_out = ChatOutput(_id="NoRAG-ChatOutput")
    no_rag_out.set(input_value=no_rag_llm.text_response, sender_name="Without RAG (LLM only)")

    # 3b. "After" lane: Retrieval -> Prompt with context -> Generation
    # Same node ingests (deduplicated, so only new chunks get embedded) and then searches.
    embeddings = OllamaEmbeddingsComponent(_id="Embeddings-Ollama")
    embeddings.set(base_url=OLLAMA_URL, model_name=EMBED_MODEL)
    retriever = ChromaVectorStoreComponent(_id="VectorStore-Chroma")
    retriever.set(
        collection_name=COLLECTION,
        persist_directory=CHROMA_DIR,
        ingest_data=splitter.split_text,
        embedding=embeddings.build_embeddings,
        search_query=chat_input.message_response,
        search_type="Similarity",
        number_of_results=4,
    )
    context_parser = ParserComponent(_id="Context-Parser")
    context_parser.set(
        input_data=retriever.search_documents,
        mode="Parser",
        pattern="[source: {file_path}]\n{text}\n",
        sep="\n---\n",
    )
    rag_prompt = PromptComponent(_id="RAG-Prompt")
    rag_prompt.set(
        template=RAG_TEMPLATE,
        persona=SYSTEM_PERSONA,
        context=context_parser.parse_combined_text,
        question=chat_input.message_response,
    )
    rag_llm = _llm("RAG-Ollama")
    rag_llm.set(input_value=rag_prompt.build_prompt)
    rag_out = ChatOutput(_id="RAG-ChatOutput")
    rag_out.set(input_value=rag_llm.text_response, sender_name="With RAG (grounded)")

    graph = Graph(chat_input, rag_out, flow_name="Onboarding RAG - Before vs After")
    graph.add_component(no_rag_out)
    return graph


# Canvas positions used by scripts/export_flows.py when generating the importable JSON.
LAYOUT = {
    "Loader-Directory": (0, 0),
    "Splitter-SplitText": (420, 0),
    "Embeddings-Ollama": (420, 520),
    "VectorStore-Chroma": (840, 120),
    "Context-Parser": (1260, 120),
    "RAG-Prompt": (1680, 120),
    "RAG-Ollama": (2100, 120),
    "RAG-ChatOutput": (2520, 120),
    "Question-ChatInput": (0, 1050),
    "NoRAG-Prompt": (1680, 1050),
    "NoRAG-Ollama": (2100, 1050),
    "NoRAG-ChatOutput": (2520, 1050),
}

NOTES = [
    (
        (0, -420),
        "blue",
        "## 1. Ingestion: Loader -> Splitter -> Embeddings\n\n"
        "- **Directory** loads `./sample_data` (swap in **URL** or **Confluence** for private docs).\n"
        "- **Split Text** cuts documents into ~800 character chunks with 150 overlap.\n"
        "- **Ollama Embeddings** (`nomic-embed-text`) turns each chunk into a vector.",
    ),
    (
        (840, -420),
        "amber",
        "## 2. Retrieval + 3. Generation (AFTER RAG)\n\n"
        "- **Chroma** stores the vectors (deduplicated) and returns the top 4 chunks for the question.\n"
        "- **Parser** formats chunks + source file into a context block.\n"
        "- **Prompt** forces the model to answer ONLY from that context.",
    ),
    (
        (1680, 700),
        "rose",
        "## BEFORE RAG: LLM only\n\nSame question, same model, same persona - but no company context. "
        "Watch it guess or give generic answers.",
    ),
]

graph = build_graph()
