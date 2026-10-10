"""Generate Langflow-importable JSON files from the Python flow definitions in flows/*.py.

Usage (from the project root):  python scripts/export_flows.py
                               python scripts/export_flows.py --flow harborpay_onboarding_rag
"""

import argparse
import importlib.util
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLOWS = {
    "onboarding_rag": "Hands-on: loader, splitter, embeddings, retrieval and generation, with a side-by-side "
    "'Without RAG' vs 'With RAG' comparison. Local Ollama models + Chroma.",
    "advanced_onboarding_rag": "Showcase: conversational memory, query rewriting, multi-query, hybrid dense (MMR) + "
    "sparse (BM25) search with RRF, cross-encoder reranking, citations and an LLM-as-judge grounding gate.",
    "harborpay_onboarding_rag": "HarborPay payment-gateway project onboarding for QA, developers, BAs and managers. "
    "Local Ollama + isolated Chroma store, source-grounded answers and visible retrieved evidence.",
}


def _handle(d: dict) -> str:
    # Langflow encodes edge handles as JSON with quotes replaced by "œ".
    return json.dumps(d).replace('"', "œ")


def _load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "flows" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export(name: str, description: str) -> Path:
    module = _load_module(name)
    graph = module.build_graph()
    graph.raw_graph_data = {"nodes": [], "edges": []}
    dumped = graph.dump(name=graph.flow_name, description=description)

    nodes = []
    for node in dumped["data"]["nodes"]:
        model_field = node["data"]["node"]["template"].get("model_name")
        # Ollama dropdowns start empty until refreshed; seed them so the UI shows the chosen model.
        if model_field and model_field.get("value") and not model_field.get("options"):
            model_field["options"] = [model_field["value"]]
        x, y = module.LAYOUT.get(node["id"], (0, 0))
        nodes.append(
            {
                "id": node["id"],
                "type": "genericNode",
                "position": {"x": x, "y": y},
                "data": node["data"],
                "selected": False,
                "dragging": False,
            }
        )
    for i, (pos, color, text) in enumerate(module.NOTES):
        note_id = f"note-{name}-{i}"
        nodes.append(
            {
                "id": note_id,
                "type": "noteNode",
                "position": {"x": pos[0], "y": pos[1]},
                "width": 400,
                "height": 330,
                "data": {
                    "id": note_id,
                    "type": "note",
                    "node": {
                        "description": text,
                        "display_name": "",
                        "documentation": "",
                        "template": {"backgroundColor": color},
                    },
                },
            }
        )

    edges = []
    # graph._edges also holds edges of components added after construction; graph.edges does not.
    for edge in graph._edges:
        source_handle = edge["data"]["sourceHandle"]
        target_handle = edge["data"]["targetHandle"]
        edges.append(
            {
                "id": f"reactflow__edge-{edge['source']}{_handle(source_handle)}-{edge['target']}{_handle(target_handle)}",
                "source": edge["source"],
                "target": edge["target"],
                "sourceHandle": _handle(source_handle),
                "targetHandle": _handle(target_handle),
                "data": edge["data"],
                "animated": False,
                "className": "",
                "selected": False,
            }
        )

    flow = {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"ragdemo/{name}")),
        "name": dumped["name"],
        "description": description,
        "endpoint_name": name.replace("_", "-"),
        "is_component": False,
        "tags": ["rag", "onboarding", "ollama"],
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.45}},
    }
    out = ROOT / "flows" / f"{name}.json"
    out.write_text(json.dumps(flow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flow", choices=FLOWS, help="Export only this flow; by default export all flows.")
    args = parser.parse_args()
    selected = {args.flow: FLOWS[args.flow]} if args.flow else FLOWS
    for flow_name, flow_description in selected.items():
        print(f"Exported {export(flow_name, flow_description).relative_to(ROOT)}", file=sys.stderr)
