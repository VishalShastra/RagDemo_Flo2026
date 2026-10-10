"""Advanced Onboarding RAG (presenter-only showcase).

Conversational memory -> query rewriting -> multi-query expansion -> hybrid dense (MMR) + sparse (BM25)
retrieval with RRF fusion -> cross-encoder reranking -> grounded answer with citations -> LLM-as-judge
grounding check.

Run without the UI:  lfx run flows/advanced_onboarding_rag.py "What is the fix for ORB-1427?"
"""

import os
import sys
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from components.cross_encoder_reranker import CrossEncoderRerankerComponent
from components.grounding_gate import GroundingGateComponent
from components.hybrid_retriever import HybridRetrieverComponent
from lfx.components.files_and_knowledge.directory import DirectoryComponent
from lfx.components.input_output import ChatInput, ChatOutput, TextOutputComponent
from lfx.components.models_and_agents import MemoryComponent, PromptComponent
from lfx.components.ollama import ChatOllamaComponent, OllamaEmbeddingsComponent
from lfx.components.processing import CombineTextComponent
from lfx.components.processing.split_text import SplitTextComponent
from lfx.graph import Graph

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text:latest")
DOCS_PATH = os.getenv("DOCS_PATH", "./sample_data")

REWRITE_TEMPLATE = dedent(
    """\
    Rewrite the latest user question into a standalone question that can be understood without the chat history.
    Resolve pronouns and references like "it", "that" or "what about contractors" using the history.
    If it is already standalone, return it unchanged. Output ONLY the rewritten question.

    Chat history:
    {history}

    Latest question: {question}
    Standalone question:"""
)

MULTI_QUERY_TEMPLATE = dedent(
    """\
    Generate 2 alternative search queries for the question below to improve document retrieval.
    Use different wording and synonyms, keep exact identifiers (ticket keys, product names) unchanged.
    Output one query per line, no numbering, no extra text.

    Question: {question}"""
)

ANSWER_TEMPLATE = dedent(
    """\
    You are the onboarding assistant for Orbitly Systems.
    Answer using ONLY the numbered context passages. Cite passages inline like [1] or [2].
    If the context does not contain the answer, reply exactly: "I don't know based on the onboarding docs."
    Be concise.

    Context:
    {context}

    Conversation so far:
    {history}

    Question: {question}
    Answer:"""
)

JUDGE_TEMPLATE = dedent(
    """\
    You are a strict fact-checker. Decide if EVERY factual claim in the answer is supported by the context.
    An answer that says "I don't know" is NOT grounded.
    Respond with JSON only: {{"grounded": true or false, "reason": "<one short sentence>"}}

    Context:
    {context}

    Answer:
    {answer}"""
)


def _llm(node_id: str, temperature: float = 0.1) -> ChatOllamaComponent:
    llm = ChatOllamaComponent(_id=node_id)
    llm.set(base_url=OLLAMA_URL, model_name=LLM_MODEL, temperature=temperature)
    return llm


def build_graph() -> Graph:
    chat_input = ChatInput(_id="Question-ChatInput")

    # Conversational memory + query rewriting
    memory = MemoryComponent(_id="Memory-History")
    memory.set(mode="Retrieve", n_messages=6, order="Ascending")
    rewrite_prompt = PromptComponent(_id="Rewrite-Prompt")
    rewrite_prompt.set(template=REWRITE_TEMPLATE, history=memory.retrieve_messages_as_text, question=chat_input.message_response)
    rewrite_llm = _llm("Rewrite-Ollama", temperature=0.0)
    rewrite_llm.set(input_value=rewrite_prompt.build_prompt)

    # Multi-query expansion
    mq_prompt = PromptComponent(_id="MultiQuery-Prompt")
    mq_prompt.set(template=MULTI_QUERY_TEMPLATE, question=rewrite_llm.text_response)
    mq_llm = _llm("MultiQuery-Ollama", temperature=0.3)
    mq_llm.set(input_value=mq_prompt.build_prompt)
    all_queries = CombineTextComponent(_id="Queries-Combine")
    all_queries.set(text1=rewrite_llm.text_response, text2=mq_llm.text_response, delimiter="\n")

    # Ingestion + hybrid retrieval
    loader = DirectoryComponent(_id="Loader-Directory")
    loader.set(path=DOCS_PATH, types=["md", "txt"])
    splitter = SplitTextComponent(_id="Splitter-SplitText")
    splitter.set(data_inputs=loader.as_dataframe, chunk_size=600, chunk_overlap=100, separator="\n\n")
    embeddings = OllamaEmbeddingsComponent(_id="Embeddings-Ollama")
    embeddings.set(base_url=OLLAMA_URL, model_name=EMBED_MODEL)
    retriever = HybridRetrieverComponent(_id="Hybrid-Retriever")
    retriever.set(chunks=splitter.split_text, embedding=embeddings.build_embeddings, queries=all_queries.combine_texts)

    # Reranking + context building
    reranker = CrossEncoderRerankerComponent(_id="Reranker")
    reranker.set(query=rewrite_llm.text_response, documents=retriever.retrieve, top_n=4)

    # Grounded generation
    answer_prompt = PromptComponent(_id="Answer-Prompt")
    answer_prompt.set(
        template=ANSWER_TEMPLATE,
        context=reranker.build_context,
        history=memory.retrieve_messages_as_text,
        question=rewrite_llm.text_response,
    )
    answer_llm = _llm("Answer-Ollama")
    answer_llm.set(input_value=answer_prompt.build_prompt)

    # Grounding check (LLM-as-judge) + gate
    judge_prompt = PromptComponent(_id="Judge-Prompt")
    judge_prompt.set(template=JUDGE_TEMPLATE, context=reranker.build_context, answer=answer_llm.text_response)
    judge_llm = _llm("Judge-Ollama", temperature=0.0)
    judge_llm.set(input_value=judge_prompt.build_prompt)
    gate = GroundingGateComponent(_id="Grounding-Gate")
    gate.set(answer=answer_llm.text_response, verdict=judge_llm.text_response)

    chat_output = ChatOutput(_id="Final-ChatOutput")
    chat_output.set(input_value=gate.gate, sender_name="Advanced RAG")

    # Debug outputs so each stage is visible on the canvas without polluting chat memory
    debug_queries = TextOutputComponent(_id="Debug-Queries")
    debug_queries.set(input_value=all_queries.combine_texts)
    debug_retrieval = TextOutputComponent(_id="Debug-RetrievalTrace")
    debug_retrieval.set(input_value=retriever.build_trace)
    debug_rerank = TextOutputComponent(_id="Debug-RerankTrace")
    debug_rerank.set(input_value=reranker.build_trace)

    graph = Graph(chat_input, chat_output, flow_name="Advanced Onboarding RAG (Showcase)")
    for component in (debug_queries, debug_retrieval, debug_rerank):
        graph.add_component(component)
    return graph


LAYOUT = {
    "Question-ChatInput": (0, 0),
    "Memory-History": (0, 450),
    "Rewrite-Prompt": (420, 150),
    "Rewrite-Ollama": (840, 150),
    "MultiQuery-Prompt": (1260, -250),
    "MultiQuery-Ollama": (1680, -250),
    "Queries-Combine": (2100, -100),
    "Debug-Queries": (2520, -400),
    "Loader-Directory": (840, 900),
    "Splitter-SplitText": (1260, 900),
    "Embeddings-Ollama": (1680, 1300),
    "Hybrid-Retriever": (2100, 650),
    "Debug-RetrievalTrace": (2520, 1150),
    "Reranker": (2520, 350),
    "Debug-RerankTrace": (2940, 900),
    "Answer-Prompt": (2940, 0),
    "Answer-Ollama": (3360, 0),
    "Judge-Prompt": (3780, 450),
    "Judge-Ollama": (4200, 450),
    "Grounding-Gate": (4620, 100),
    "Final-ChatOutput": (5040, 100),
}

NOTES = [
    (
        (0, -650),
        "blue",
        "## 1. Conversational memory + query rewriting\n\n"
        "**Message History** feeds the last 6 turns to a rewriter so follow-ups like "
        "*'what about contractors?'* become standalone questions before retrieval.",
    ),
    (
        (1260, -700),
        "amber",
        "## 2. Multi-query expansion\n\nThe LLM writes 2 paraphrases. Each query is searched and the results are "
        "fused, which improves recall when users phrase things differently from the docs.",
    ),
    (
        (1260, 1350),
        "lime",
        "## 3. Hybrid search: dense + sparse\n\n"
        "- **Dense** (Chroma, **MMR**): semantic match, diversified to avoid near-duplicate chunks.\n"
        "- **Sparse** (**BM25**): exact keywords such as `ORB-1427` or `OrbitGate`.\n"
        "- **Reciprocal Rank Fusion** merges both rankings. Optional metadata filter on source.",
    ),
    (
        (2940, -500),
        "rose",
        "## 4. Rerank -> 5. Grounded answer -> 6. Grounding check\n\n"
        "- **Cross-encoder** (FlashRank, local CPU) re-scores question+chunk pairs and keeps top 4.\n"
        "- Answer cites passages [1], [2] and must say *I don't know* if unsupported.\n"
        "- **LLM-as-judge** verifies faithfulness; the **Grounding Gate** blocks unsupported answers.",
    ),
]

graph = build_graph()
