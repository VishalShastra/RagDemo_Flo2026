from __future__ import annotations

import re

from lfx.custom.custom_component.component import Component
from lfx.io import DropdownInput, HandleInput, IntInput, MessageTextInput, Output, StrInput
from lfx.schema.data import Data
from lfx.schema.message import Message


class CrossEncoderRerankerComponent(Component):
    display_name = "Cross-Encoder Reranker"
    description = (
        "Re-scores retrieved chunks against the question with a local cross-encoder (FlashRank, CPU, no API key), "
        "removes near-duplicates and builds a numbered, citation-ready context within a size budget."
    )
    icon = "list-ordered"
    name = "CrossEncoderReranker"

    inputs = [
        MessageTextInput(name="query", display_name="Question", info="Standalone question used for reranking."),
        HandleInput(name="documents", display_name="Retrieved Chunks", input_types=["Data"], is_list=True),
        DropdownInput(
            name="model_name",
            display_name="Reranker Model",
            options=["ms-marco-MiniLM-L-12-v2", "ms-marco-TinyBERT-L-2-v2", "rank-T5-flan"],
            value="ms-marco-MiniLM-L-12-v2",
        ),
        IntInput(name="top_n", display_name="Keep Top N", value=4),
        IntInput(name="max_context_chars", display_name="Context Budget (chars)", value=4000, advanced=True),
        StrInput(name="cache_dir", display_name="Model Cache Dir", value="./.flashrank_cache", advanced=True),
    ]

    outputs = [
        Output(display_name="Context", name="context", method="build_context"),
        Output(display_name="Reranked Chunks", name="reranked", method="rerank"),
        Output(display_name="Rerank Trace", name="trace", method="build_trace"),
    ]

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\W+", " ", text.lower()).strip()

    def _run(self) -> tuple[list[Data], str]:
        if getattr(self, "_cached", None) is not None:
            return self._cached

        docs = [d for d in (self.documents or []) if isinstance(d, Data)]
        seen: set[str] = set()
        unique: list[Data] = []
        for doc in docs:
            key = self._normalize(doc.get_text())[:300]
            if key not in seen:
                seen.add(key)
                unique.append(doc)

        trace = [f"Input chunks: {len(docs)}, after de-duplication: {len(unique)}"]
        try:
            from flashrank import Ranker, RerankRequest

            ranker = Ranker(model_name=self.model_name, cache_dir=self.cache_dir)
            passages = [{"id": i, "text": d.get_text()} for i, d in enumerate(unique)]
            ranked = ranker.rerank(RerankRequest(query=str(self.query), passages=passages))
            order = [(int(r["id"]), float(r["score"])) for r in ranked]
            trace.append(f"Reranker: {self.model_name}")
        except ImportError:
            order = [(i, 0.0) for i in range(len(unique))]
            trace.append("flashrank not installed - kept fusion order (pip install flashrank)")

        reranked: list[Data] = []
        for new_rank, (idx, score) in enumerate(order[: self.top_n], start=1):
            doc = unique[idx]
            data = dict(doc.data)
            data.update({"rerank_score": round(score, 4), "rerank_position": new_rank, "fusion_position": idx + 1})
            reranked.append(Data(text=doc.get_text(), data=data))
            trace.append(
                f"  #{new_rank} (was #{idx + 1}) score={score:.3f} {str(data.get('source', '')).split('/')[-1]}"
            )
        self._cached = (reranked, "\n".join(trace))
        return self._cached

    def rerank(self) -> list[Data]:
        reranked, _ = self._run()
        self.status = reranked
        return reranked

    def build_context(self) -> Message:
        reranked, _ = self._run()
        blocks: list[str] = []
        used = 0
        for i, doc in enumerate(reranked, start=1):
            source = str(doc.data.get("source", "unknown")).split("/")[-1]
            block = f"[{i}] (source: {source})\n{doc.get_text().strip()}"
            if used + len(block) > self.max_context_chars:
                break
            blocks.append(block)
            used += len(block)
        context = "\n\n".join(blocks) if blocks else "NO RELEVANT CONTEXT FOUND"
        self.status = context
        return Message(text=context)

    def build_trace(self) -> Message:
        _, trace = self._run()
        self.status = trace
        return Message(text=trace)
