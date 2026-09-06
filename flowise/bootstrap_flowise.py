#!/usr/bin/env python3
"""Create the three course Chatflows through Flowise's authenticated API.

The input is an exported Flowise Chatflow JSON. Keeping the visual template in
Flowise makes this bootstrap compatible with the installed Flowise version,
while this script owns the environment-specific wiring and prompts.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


FLOW_PROMPTS = {
    "storage-course-qa": (
        "你是电力系统储能技术课程助教。只能依据检索到的课程资料回答。"
        "回答必须使用中文；如果资料不足，明确说资料不足，不得编造文件、页码、实验数据或文献。"
        "回答末尾列出来源文件和页码。\n\n课程资料：\n{context}"
    ),
    "storage-learning-path": (
        "你是电力系统储能技术课程学习规划助手。只能推荐检索结果中存在的章节、知识点和课件。"
        "请根据学生薄弱点、可用时间和目标，输出有顺序的学习计划，并为每项任务附来源文件和页码。"
        "资料不足时先说明缺口，不得虚构资源。\n\n课程资料：\n{context}"
    ),
    "storage-teacher-assistant": (
        "你是电力系统储能技术课程教师助理。备课、试题和评分依据必须来自检索到的课程资料。"
        "输出结构化结果，标注来源文件和页码；资料不足时明确说明，不得编造引用或实验数据。"
        "\n\n课程资料：\n{context}"
    ),
}


def replace_strings(value: Any, replacements: dict[str, str]) -> Any:
    """Replace node IDs recursively, including edge handles from exports."""
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: replace_strings(item, replacements) for key, item in value.items()}
    return value


def node_name(node: dict[str, Any]) -> str:
    data = node.get("data") or {}
    return str(data.get("name") or node.get("id") or "")


def set_credential(data: dict[str, Any], credential_id: str | None) -> None:
    if credential_id:
        data["credential"] = credential_id


def transform_flow(
    template: dict[str, Any],
    flow_name: str,
    *,
    llm_base_path: str,
    llm_model: str,
    embedding_base_path: str,
    embedding_model: str,
    qdrant_url: str,
    qdrant_collection: str,
    qdrant_dimension: int,
    openai_credential_id: str | None,
    qdrant_credential_id: str | None,
) -> dict[str, Any]:
    """Convert an official RAG template into a course-specific flow graph."""
    flow = copy.deepcopy(template)
    replacements = {"faiss_0": "qdrant_0", "chatMistralAI_0": "chatOpenAI_0"}
    flow = replace_strings(flow, replacements)
    nodes = []
    removed_names = {"textFile", "documentStore", "recursiveCharacterTextSplitter", "stickyNote"}

    for node in flow.get("nodes", []):
        data = node.setdefault("data", {})
        name = node_name(node)
        if name in removed_names:
            continue

        if name in {"chatMistralAI", "chatOpenAI"} or data.get("type") in {"ChatMistralAI", "ChatOpenAI"}:
            data.update({"id": "chatOpenAI_0", "name": "chatOpenAI", "type": "ChatOpenAI", "label": "OpenAI"})
            inputs = data.setdefault("inputs", {})
            inputs.update(
                {
                    "modelName": llm_model,
                    "temperature": 0.1,
                    "streaming": True,
                    "basepath": llm_base_path,
                    # The gateway authenticates its own upstream. This dummy
                    # value prevents a client library from rejecting an empty key.
                    "openAIApiKey": "flowise-internal-gateway",
                }
            )
            set_credential(data, openai_credential_id)

        elif name in {"openAIEmbeddings", "localAIEmbeddings"} or data.get("type") == "OpenAIEmbeddings":
            data.update({"id": "openAIEmbeddings_0", "name": "openAIEmbeddings", "type": "OpenAIEmbeddings"})
            inputs = data.setdefault("inputs", {})
            inputs.update(
                {
                    "modelName": embedding_model,
                    "basepath": embedding_base_path,
                    "dimensions": qdrant_dimension,
                }
            )
            set_credential(data, openai_credential_id)

        elif name in {"faiss", "qdrant"} or data.get("type") in {"Faiss", "Qdrant"}:
            data.update({"id": "qdrant_0", "name": "qdrant", "type": "Qdrant", "label": "Qdrant"})
            inputs = data.setdefault("inputs", {})
            inputs.update(
                {
                    "document": "",
                    "embeddings": "{{openAIEmbeddings_0.data.instance}}",
                    "qdrantServerUrl": qdrant_url,
                    "qdrantCollection": qdrant_collection,
                    "qdrantVectorDimension": qdrant_dimension,
                    "contentPayloadKey": "content",
                    "metadataPayloadKey": "metadata",
                    "qdrantSimilarity": "Cosine",
                    "topK": 4,
                }
            )
            set_credential(data, qdrant_credential_id)

        elif name == "conversationalRetrievalQAChain" or data.get("type") == "ConversationalRetrievalQAChain":
            inputs = data.setdefault("inputs", {})
            inputs.update(
                {
                    "model": "{{chatOpenAI_0.data.instance}}",
                    "vectorStoreRetriever": "{{qdrant_0.data.instance}}",
                    "returnSourceDocuments": True,
                    "responsePrompt": FLOW_PROMPTS[flow_name],
                }
            )

        nodes.append(node)

    valid_ids = {str(node.get("id")) for node in nodes}
    edges = [
        edge
        for edge in flow.get("edges", [])
        if str(edge.get("source")) in valid_ids and str(edge.get("target")) in valid_ids
    ]
    return {"nodes": nodes, "edges": edges}


def api_request(base_url: str, token: str, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    url = base_url.rstrip("/") + "/api/v1/" + path.lstrip("/")
    request = urllib.request.Request(
        url,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
            return json.loads(payload) if payload else None
    except urllib.error.HTTPError as exc:
        # Avoid printing the provider response, which can contain credentials.
        raise RuntimeError(f"Flowise API {method} {path} returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Flowise API unavailable: {exc.reason}") from exc


def upsert_flow(base_url: str, token: str, name: str, flow_data: dict[str, Any]) -> str:
    existing = api_request(base_url, token, "GET", "chatflows") or []
    current = next((item for item in existing if item.get("name") == name), None)
    payload = {
        "name": name,
        "flowData": json.dumps(flow_data, ensure_ascii=False),
        "deployed": True,
        # The browser calls only the prediction endpoint. Flowise's admin
        # routes remain internal and protected by the application login.
        "isPublic": True,
        "type": "CHATFLOW",
        "category": "storage-course",
    }
    if current:
        result = api_request(base_url, token, "PUT", f"chatflows/{current['id']}", payload)
    else:
        result = api_request(base_url, token, "POST", "chatflows", payload)
    return str((result or {}).get("id") or (current or {}).get("id") or "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, type=argparse.FileType("r", encoding="utf-8"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    template = json.load(args.template)
    base_url = os.getenv("FLOWISE_BASE_URL", "http://127.0.0.1:3000")
    token = os.getenv("FLOWISE_API_TOKEN", "")
    if not args.dry_run and not token:
        raise SystemExit("FLOWISE_API_TOKEN is required unless --dry-run is used")

    common = {
        "llm_base_path": os.getenv("LLM_FLOWISE_BASE_PATH", "http://model-gateway:8080/v1"),
        "llm_model": os.getenv("LLM_MODEL", "mock-model"),
        "embedding_base_path": os.getenv("EMBEDDING_FLOWISE_BASE_PATH", "http://model-gateway:8080/v1"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "mock-embedding"),
        "qdrant_url": os.getenv("QDRANT_FLOWISE_URL", "http://qdrant:6333"),
        "qdrant_collection": os.getenv("QDRANT_COLLECTION", "storage-course-v1"),
        "qdrant_dimension": int(os.getenv("QDRANT_VECTOR_DIMENSION", "64")),
        "openai_credential_id": os.getenv("FLOWISE_OPENAI_CREDENTIAL_ID") or None,
        "qdrant_credential_id": os.getenv("FLOWISE_QDRANT_CREDENTIAL_ID") or None,
    }
    if not common["qdrant_credential_id"] and os.getenv("REQUIRE_QDRANT_CREDENTIAL", "true").lower() in {"1", "true", "yes"}:
        raise SystemExit("FLOWISE_QDRANT_CREDENTIAL_ID is required; do not put Qdrant API keys in flowData")

    flow_ids: dict[str, str] = {}
    for name in FLOW_PROMPTS:
        graph = transform_flow(template, name, **common)
        if args.dry_run:
            print(json.dumps({"name": name, "nodes": [node.get("id") for node in graph["nodes"]], "edges": len(graph["edges"])}, ensure_ascii=False))
        else:
            flow_id = upsert_flow(base_url, token, name, graph)
            flow_ids[name] = flow_id
            print(json.dumps({"name": name, "id": flow_id, "deployed": True}, ensure_ascii=False))
    if not args.dry_run and os.getenv("AGENT_CONFIG_PATH"):
        config_path = os.environ["AGENT_CONFIG_PATH"]
        with open(config_path, "w", encoding="utf-8") as output:
            output.write("// Generated by flowise/bootstrap_flowise.py. Do not put secrets here.\n")
            output.write("window.AGENT_CONFIG = ")
            json.dump(
                {"flows": {"qa": flow_ids.get("storage-course-qa", ""), "learningPath": flow_ids.get("storage-learning-path", ""), "teacherAssistant": flow_ids.get("storage-teacher-assistant", "")}},
                output,
                ensure_ascii=False,
            )
            output.write(";\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
