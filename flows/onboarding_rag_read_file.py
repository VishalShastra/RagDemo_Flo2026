"""Onboarding RAG flow using Langflow's current Read File component.

Select the Markdown files from sample_data in the Read File node before running.
"""

import os
from textwrap import dedent

from lfx.components.chroma import ChromaVectorStoreComponent
from lfx.components.files_and_knowledge.file import FileComponent
from lfx.components.input_output import ChatInput, ChatOutput
from lfx.components.models_and_agents import PromptComponent
from lfx.components.ollama import ChatOllamaComponent, OllamaEmbeddingsComponent
from lfx.components.processing import ParserComponent
from lfx.components.processing.split_text import SplitTextComponent
from lfx.graph import Graph
from lfx.io import Output

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text:latest")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db_read_file")
COLLECTION = "onboarding_docs_read_file"

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


class MultiFileReadComponent(FileComponent):
    """Expose Read File's multi-file DataFrame output to the flow graph."""

    display_name = "Read File"
    name = "ReadFile"
    outputs = [Output(display_name="Files", name="dataframe", method="load_files")]


def _llm(node_id: str) -> ChatOllamaComponent:
    llm = ChatOllamaComponent(_id=node_id)
    llm.set(base_url=OLLAMA_URL, model_name=LLM_MODEL, temperature=0.1)
    return llm


def build_graph() -> Graph:
    chat_input = ChatInput(_id="Question-ChatInput")

    loader = MultiFileReadComponent(_id="Loader-ReadFile")

    splitter = SplitTextComponent(_id="Splitter-SplitText")
    splitter.set(data_inputs=loader.load_files, chunk_size=800, chunk_overlap=150, separator="\n\n")

    no_rag_prompt = PromptComponent(_id="NoRAG-Prompt")
    no_rag_prompt.set(template=NO_RAG_TEMPLATE, persona=SYSTEM_PERSONA, question=chat_input.message_response)
    no_rag_llm = _llm("NoRAG-Ollama")
    no_rag_llm.set(input_value=no_rag_prompt.build_prompt)
    no_rag_out = ChatOutput(_id="NoRAG-ChatOutput")
    no_rag_out.set(input_value=no_rag_llm.text_response, sender_name="Without RAG (LLM only)")

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

    graph = Graph(chat_input, rag_out, flow_name="Onboarding RAG - Before vs After (Read File)")
    graph.add_component(no_rag_out)
    return graph


LAYOUT = {
    "Loader-ReadFile": (0, 0),
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
        "## 1. Load and split documents\n\n"
        "- In **Read File**, select all the Markdown files from `sample_data`. This component accepts selected files, not a directory path.\n"
        "- Its **Files** output preserves each file's path and text for citations.\n"
        "- **Split Text** creates ~800-character chunks with 150 characters of overlap.",
    ),
    (
        (840, -420),
        "amber",
        "## 2. Retrieve and answer with RAG\n\n"
        "- **Chroma** embeds and stores the chunks, then returns the top 4 for the question.\n"
        "- **Parser** formats the retrieved text with its source file.\n"
        "- The grounded prompt tells the model to answer only from that context.",
    ),
    (
        (1680, 1470),
        "green",
        "## 3. Compare both answers\n\n"
        "- **Without RAG** sends the question directly to the LLM.\n"
        "- **With RAG** adds the retrieved onboarding context.\n"
        "- Both outputs use the same local Ollama model for a fair comparison.",
    ),
]