"""Structural checks for the HarborPay graph/export; no Ollama calls or database writes."""

import importlib.util
import json
import os
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HarborPayFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment = patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "LLM_MODEL": "qwen2.5:3b",
                "EMBED_MODEL": "nomic-embed-text:latest",
                "DOCS_PATH": "./sample_data",
                "HARBORPAY_CHROMA_DIR": "./chroma_db_harborpay",
                "CHROMA_DIR": "./old-index-must-not-be-used",
            },
        )
        cls.environment.start()
        cls.addClassCleanup(cls.environment.stop)
        cls.flow = load_module("test_harborpay", ROOT / "flows" / "harborpay_onboarding_rag.py")
        cls.exporter = load_module("test_exporter", ROOT / "scripts" / "export_flows.py")

    def exported_flow(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "flows").mkdir()
            with patch.object(self.exporter, "ROOT", root), patch.object(
                self.exporter, "_load_module", return_value=self.flow
            ):
                result = self.exporter.export(
                    "harborpay_onboarding_rag", self.exporter.FLOWS["harborpay_onboarding_rag"]
                )
            return json.loads(result.read_text(encoding="utf-8"))

    def test_pipeline_and_evidence_edges(self):
        flow = self.exported_flow()
        actual = {
            (edge["source"], edge["target"], edge["data"]["targetHandle"]["fieldName"])
            for edge in flow["data"]["edges"]
        }
        expected = {
            ("HarborPay-Documents", "HarborPay-Chunks", "data_inputs"),
            ("HarborPay-Chunks", "HarborPay-Knowledge", "ingest_data"),
            ("HarborPay-Embeddings", "HarborPay-Knowledge", "embedding"),
            ("HarborPay-Question", "HarborPay-Knowledge", "search_query"),
            ("HarborPay-Knowledge", "HarborPay-Context", "input_data"),
            ("HarborPay-Context", "HarborPay-Prompt", "context"),
            ("HarborPay-Question", "HarborPay-Prompt", "question"),
            ("HarborPay-Prompt", "HarborPay-AnswerModel", "input_value"),
            ("HarborPay-AnswerModel", "HarborPay-SourceAnswer", "answer"),
            ("HarborPay-Context", "HarborPay-SourceAnswer", "context"),
            ("HarborPay-SourceAnswer", "HarborPay-Answer", "input_value"),
            ("HarborPay-Context", "HarborPay-Evidence", "input_value"),
        }
        self.assertEqual(actual, expected)
        nodes = {node["id"] for node in flow["data"]["nodes"] if node["type"] == "genericNode"}
        self.assertEqual(nodes, set(self.flow.LAYOUT))
        for edge in flow["data"]["edges"]:
            self.assertIn(edge["source"], nodes)
            self.assertIn(edge["target"], nodes)
            self.assertEqual(
                json.loads(edge["sourceHandle"].replace("\u0153", '"')), edge["data"]["sourceHandle"]
            )

    def test_settings_and_isolated_storage(self):
        flow = self.exported_flow()
        fields = {
            node["id"]: node["data"]["node"]["template"]
            for node in flow["data"]["nodes"]
            if node["type"] == "genericNode"
        }
        store = fields["HarborPay-Knowledge"]
        self.assertEqual(store["persist_directory"]["value"], "./chroma_db_harborpay")
        self.assertEqual(store["collection_name"]["value"], "harborpay_project_onboarding")
        self.assertEqual(store["number_of_results"]["value"], 6)
        self.assertFalse(store["allow_duplicates"]["value"])
        self.assertFalse(fields["HarborPay-Documents"]["silent_errors"]["value"])
        self.assertFalse(fields["HarborPay-Evidence"]["should_store_message"]["value"])
        self.assertEqual(fields["HarborPay-Chunks"]["chunk_size"]["value"], 1200)
        self.assertEqual(fields["HarborPay-Chunks"]["chunk_overlap"]["value"], 200)
        self.assertEqual(fields["HarborPay-AnswerModel"]["num_ctx"]["value"], 8192)
        self.assertIn("{file_path}", fields["HarborPay-Context"]["pattern"]["value"])
        self.assertEqual(flow["endpoint_name"], "harborpay-onboarding-rag")

    def test_prompt_scope_and_missing_evidence_policy(self):
        prompt = self.flow.RAG_TEMPLATE.format(
            persona=self.flow.SYSTEM_PERSONA,
            context="[source: example.md]\nSynthetic evidence",
            question="Who approves business rules?",
        )
        self.assertIn("HarborPay Gateway", prompt)
        self.assertIn("ONLY the retrieved project context", prompt)
        self.assertIn("I don't know based on the HarborPay project docs.", prompt)
        self.assertIn("[source: filename.md]", prompt)
        self.assertIn("fictional", prompt)
        self.assertNotIn("Orbitly", prompt)

    def test_custom_harborpay_store(self):
        with patch.dict(os.environ, {"HARBORPAY_CHROMA_DIR": "./chroma_db_harborpay/test-version"}):
            custom = load_module("test_harborpay_override", ROOT / "flows" / "harborpay_onboarding_rag.py")
        self.assertEqual(custom.CHROMA_DIR, "./chroma_db_harborpay/test-version")

    def test_committed_export_matches_generator(self):
        generated = self.exported_flow()
        committed = json.loads(
            (ROOT / "flows" / "harborpay_onboarding_rag.json").read_text(encoding="utf-8")
        )
        # Prompt construction creates a Message timestamp at export time.
        for flow in (generated, committed):
            model = next(node for node in flow["data"]["nodes"] if node["id"] == "HarborPay-AnswerModel")
            value = model["data"]["node"]["template"]["input_value"]["value"]
            value.pop("timestamp")
            value["data"].pop("timestamp")
        self.assertEqual(generated, committed)

    def test_repeated_ingestion_keeps_unique_passages(self):
        from components.project_chroma import ProjectChromaComponent
        from langchain_chroma import Chroma
        from langchain_core.embeddings import DeterministicFakeEmbedding
        from lfx.schema.data import Data

        store = Chroma(
            collection_name=f"test_harborpay_{uuid.uuid4().hex}",
            embedding_function=DeterministicFakeEmbedding(size=8),
        )
        component = ProjectChromaComponent()
        try:
            component.set(
                ingest_data=[
                    Data(data={"text": "Refund reservations count.", "file_path": "rules.md", "extra": None}),
                    Data(data={"text": "Refund reservations count.", "file_path": "rules.md", "extra": "changed"}),
                    Data(data={"text": "Manager records the decision.", "file_path": "roles.md"}),
                ]
            )
            component._add_documents_to_vector_store(store)
            first = store.get()
            component._add_documents_to_vector_store(store)
            second = store.get()
            self.assertEqual(len(first["ids"]), 2)
            self.assertEqual(set(first["ids"]), set(second["ids"]))
            self.assertEqual(len(second["ids"]), 2)
            self.assertTrue(all("file_path" in metadata for metadata in second["metadatas"]))
        finally:
            store.delete_collection()

    def test_source_footer_uses_actual_context(self):
        from components.source_answer import SourceAnswerComponent

        component = SourceAnswerComponent()
        component.set(
            answer="The model's original answer.",
            context="[source: F:\\docs\\rules.md]\nEvidence\n---\n[source: F:\\docs\\rules.md]\nMore evidence",
        )
        message = component.format_answer()
        self.assertTrue(message.text.startswith("The model's original answer."))
        self.assertEqual(message.text.count("[source: rules.md]"), 1)
        self.assertIn("does not validate every claim", message.text)
        component.set(answer="No answer found.", context="")
        self.assertIn("No source passages were retrieved", component.format_answer().text)
        component.set(answer="Answer.", context="Evidence without source metadata")
        with self.assertRaisesRegex(ValueError, "source labels"):
            component.format_answer()
        component.set(answer="", context="")
        with self.assertRaisesRegex(ValueError, "no text"):
            component.format_answer()


if __name__ == "__main__":
    unittest.main()
