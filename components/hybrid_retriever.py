from __future__ import annotations

import hashlib
import re

from lfx.custom.custom_component.component import Component
from lfx.io import DropdownInput, FloatInput, HandleInput, IntInput, MessageTextInput, Output, StrInput
from lfx.schema.data import Data
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message


class HybridRetrieverComponent(Component):
    display_name = "Hybrid Retriever (Dense + BM25)"
    description = (
        "Dense vector search (Chroma, Similarity or MMR) + sparse keyword search (BM25), "
        "fused with Reciprocal Rank Fusion. Accepts several queries (one per line) for multi-query retrieval."
    )
    icon = "git-merge"
    name = "HybridRetriever"

    inputs = [
        HandleInput(
            name="chunks",
            display_name="Chunks",
            input_types=["DataFrame", "Data"],
            is_list=True,
            info="Chunks from Split Text. New chunks are embedded into Chroma; all chunks feed the BM25 index.",
        ),
        HandleInput(name="embedding", display_name="Embedding", input_types=["Embeddings"]),
        MessageTextInput(
            name="queries",
            display_name="Queries",
            info="One query per line (output of the multi-query step).",
        ),
        StrInput(name="persist_directory", display_name="Persist Directory", value="./chroma_db_advanced"),
        StrInput(name="collection_name", display_name="Collection Name", value="onboarding_advanced"),
        DropdownInput(
            name="dense_search_type",
            display_name="Dense Search Type",
            options=["MMR", "Similarity"],
            value="MMR",
            info="MMR trades a little relevance for diversity so near-duplicate chunks are not all returned.",
        ),
        IntInput(name="k", display_name="Results per Retriever", value=8),
        IntInput(name="fetch_k", display_name="MMR Candidate Pool (fetch_k)", value=20, advanced=True),
        FloatInput(
            name="mmr_lambda",
            display_name="MMR Lambda",
            value=0.5,
            info="1.0 = pure relevance, 0.0 = pure diversity.",
            advanced=True,
        ),
        IntInput(name="rrf_k", display_name="RRF Constant", value=60, advanced=True),
        IntInput(name="top_n", display_name="Fused Results to Return", value=10),
        StrInput(
            name="source_filter",
            display_name="Metadata Filter (source contains)",
            value="",
            info="Optional: keep only chunks whose source path contains this text, e.g. 'jira' or 'leave'.",
        ),
    ]

    outputs = [
        Output(display_name="Fused Results", name="results", method="retrieve"),
        Output(display_name="Retrieval Trace", name="trace", method="build_trace"),
    ]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[a-z0-9][a-z0-9\-_.]*", text.lower())

    def _chunk_data(self) -> list[Data]:
        items: list[Data] = []
        for item in self.chunks or []:
            if isinstance(item, DataFrame):
                items.extend(item.to_data_list())
            elif isinstance(item, Data):
                items.append(item)
        return [d for d in items if (d.get_text() or "").strip()]

    @staticmethod
    def _source(data: Data) -> str:
        return str(data.data.get("file_path") or data.data.get("source") or data.data.get("url") or "unknown")

    def _chunk_id(self, data: Data) -> str:
        return hashlib.sha1(f"{self._source(data)}|{data.get_text()}".encode()).hexdigest()

    def _vector_store(self, chunks: list[Data]):
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        store = Chroma(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
            embedding_function=self.embedding,
        )
        ids = [self._chunk_id(c) for c in chunks]
        existing = set(store.get(ids=ids)["ids"]) if ids else set()
        new = [(i, c) for i, c in zip(ids, chunks, strict=True) if i not in existing]
        if new:
            store.add_documents(
                [Document(page_content=c.get_text(), metadata={"source": self._source(c)}) for _, c in new],
                ids=[i for i, _ in new],
            )
        return store

    def _run(self) -> tuple[list[Data], str]:
        if getattr(self, "_cached", None) is not None:
            return self._cached

        from rank_bm25 import BM25Okapi

        chunks = self._chunk_data()
        queries = [q.strip(" -*\t0123456789.") for q in str(self.queries or "").splitlines()]
        queries = [q for q in queries if q] or [str(self.queries or "")]
        store = self._vector_store(chunks)

        by_id = {self._chunk_id(c): c for c in chunks}
        ordered_ids = list(by_id)
        bm25 = BM25Okapi([self._tokenize(by_id[i].get_text()) for i in ordered_ids])

        rrf: dict[str, float] = {}
        best_dense: dict[str, int] = {}
        best_sparse: dict[str, int] = {}
        trace = [f"Queries ({len(queries)}): " + " | ".join(queries), ""]

        for query in queries:
            if self.dense_search_type == "MMR":
                docs = store.max_marginal_relevance_search(
                    query, k=self.k, fetch_k=self.fetch_k, lambda_mult=self.mmr_lambda
                )
            else:
                docs = store.similarity_search(query, k=self.k)
            dense_ids = [hashlib.sha1(f"{d.metadata.get('source')}|{d.page_content}".encode()).hexdigest() for d in docs]

            scores = bm25.get_scores(self._tokenize(query))
            ranked = sorted(range(len(ordered_ids)), key=lambda i: scores[i], reverse=True)
            sparse_ids = [ordered_ids[i] for i in ranked[: self.k] if scores[i] > 0]

            for rank, cid in enumerate(dense_ids, start=1):
                rrf[cid] = rrf.get(cid, 0.0) + 1.0 / (self.rrf_k + rank)
                best_dense[cid] = min(best_dense.get(cid, rank), rank)
            for rank, cid in enumerate(sparse_ids, start=1):
                rrf[cid] = rrf.get(cid, 0.0) + 1.0 / (self.rrf_k + rank)
                best_sparse[cid] = min(best_sparse.get(cid, rank), rank)

            trace.append(f"Query: {query}")
            trace.append(f"  dense ({self.dense_search_type}): {[self._short(by_id, c) for c in dense_ids[:4]]}")
            trace.append(f"  sparse (BM25): {[self._short(by_id, c) for c in sparse_ids[:4]]}")

        results: list[Data] = []
        for cid, score in sorted(rrf.items(), key=lambda kv: kv[1], reverse=True):
            chunk = by_id.get(cid)
            if chunk is None:
                continue
            source = self._source(chunk)
            if self.source_filter and self.source_filter.lower() not in source.lower():
                continue
            results.append(
                Data(
                    text=chunk.get_text(),
                    data={
                        "text": chunk.get_text(),
                        "source": source,
                        "rrf_score": round(score, 4),
                        "dense_rank": best_dense.get(cid),
                        "sparse_rank": best_sparse.get(cid),
                    },
                )
            )
            if len(results) >= self.top_n:
                break

        trace.append("")
        trace.append("Fused (RRF) order:")
        trace.extend(
            f"  {i}. {r.data['source'].split('/')[-1]} rrf={r.data['rrf_score']} "
            f"dense#{r.data['dense_rank']} bm25#{r.data['sparse_rank']}"
            for i, r in enumerate(results, start=1)
        )
        self._cached = (results, "\n".join(trace))
        return self._cached

    def _short(self, by_id: dict[str, Data], cid: str) -> str:
        chunk = by_id.get(cid)
        return self._source(chunk).split("/")[-1] if chunk else cid[:8]

    def retrieve(self) -> list[Data]:
        results, _ = self._run()
        self.status = results
        return results

    def build_trace(self) -> Message:
        _, trace = self._run()
        self.status = trace
        return Message(text=trace)
