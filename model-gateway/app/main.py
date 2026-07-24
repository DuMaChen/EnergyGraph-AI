from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse


app = FastAPI(title="Course Model Gateway", version="0.1.0")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def error_response(message: str, status_code: int, error_type: str = "upstream_error") -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "type": error_type,
                "param": None,
                "code": status_code,
            }
        },
    )


def upstream_error_type(status_code: int) -> str:
    if status_code == 401 or status_code == 403:
        return "authentication_error"
    if status_code == 429:
        return "rate_limit_error"
    if status_code >= 500:
        return "upstream_error"
    return "invalid_request_error"


def upstream_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    normalized_path = path.lstrip("/")
    # Accept both provider roots and OpenAI-compatible /v1 roots. This keeps
    # model replacement a configuration-only change.
    if base.endswith("/v1") and normalized_path.startswith("v1/"):
        normalized_path = normalized_path[3:]
    return f"{base}/{normalized_path}"


def auth_headers(api_key: str) -> dict[str, str]:
    headers = {"content-type": "application/json"}
    if api_key:
        headers["authorization"] = f"Bearer {api_key}"
    return headers


def deterministic_embedding(text: str, dimension: int) -> list[float]:
    """Stable test vector; never use this for production retrieval quality."""
    values: list[float] = []
    counter = 0
    while len(values) < dimension:
        digest = hashlib.sha256(f"{text}:{counter}".encode("utf-8")).digest()
        values.extend((byte / 127.5) - 1.0 for byte in digest)
        counter += 1
    return values[:dimension]


def mock_chat(body: dict[str, Any]) -> dict[str, Any]:
    messages = body.get("messages") or []
    user_message = next(
        (item.get("content", "") for item in reversed(messages) if item.get("role") == "user"),
        "",
    )
    content = (
        "[MOCK_MODE] 已收到课程 Agent 请求。"
        "当前使用的是流程测试模型，真实回答需要配置 OpenAI-compatible 上游。\n"
        f"问题摘要：{str(user_message)[:200]}"
    )
    return {
        "id": f"chatcmpl-mock-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.get("model") or os.getenv("LLM_MODEL", "mock-model"),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    }


@app.get("/health")
async def health() -> dict[str, Any]:
    llm_configured = bool(os.getenv("LLM_BASE_URL") and os.getenv("LLM_API_KEY"))
    embedding_configured = bool(os.getenv("EMBEDDING_BASE_URL") and os.getenv("EMBEDDING_API_KEY"))
    return {
        "status": "ok",
        "service": "course-model-gateway",
        "llm_configured": llm_configured,
        "embedding_configured": embedding_configured,
        "mock_mode": env_bool("MOCK_MODE"),
    }


@app.get("/v1/models")
async def models() -> dict[str, Any]:
    model = os.getenv("LLM_MODEL") or "unconfigured-model"
    return {
        "object": "list",
        "data": [{"id": model, "object": "model", "owned_by": "configured-upstream"}],
    }


async def proxy_json(path: str, body: dict[str, Any], base_url: str, api_key: str) -> JSONResponse:
    if not base_url:
        return error_response("Model upstream is not configured", 503, "configuration_error")
    headers = auth_headers(api_key)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=10.0)) as client:
            response = await client.post(upstream_url(base_url, path), headers=headers, json=body)
    except httpx.TimeoutException:
        return error_response("Model upstream timed out", 504, "upstream_timeout")
    except httpx.HTTPError as exc:
        return error_response(f"Model upstream unavailable: {exc.__class__.__name__}", 502, "upstream_unavailable")

    if response.status_code >= 400:
        # Do not forward provider response bodies: they may contain request
        # details, internal URLs, or accidental credential material.
        return error_response(
            f"Model upstream returned HTTP {response.status_code}",
            response.status_code,
            upstream_error_type(response.status_code),
        )

    content_type = response.headers.get("content-type", "application/json")
    if "application/json" not in content_type:
        return JSONResponse(status_code=response.status_code, content={"raw": response.text})
    try:
        payload = response.json()
    except ValueError:
        return error_response("Model upstream returned invalid JSON", 502, "invalid_upstream_response")
    return JSONResponse(status_code=response.status_code, content=payload)


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> Any:
    try:
        body = await request.json()
    except ValueError:
        return error_response("Request body must be JSON", 400, "invalid_request_error")
    if not isinstance(body, dict) or not isinstance(body.get("messages"), list) or not body["messages"]:
        return error_response("messages must be a non-empty array", 400, "invalid_request_error")
    if not isinstance(body.get("model"), str) or not body["model"].strip():
        return error_response("model must be a non-empty string", 400, "invalid_request_error")

    if env_bool("MOCK_MODE"):
        result = mock_chat(body)
        if body.get("stream"):
            text = result["choices"][0]["message"]["content"]

            def chunk(delta: dict[str, Any], finish_reason: str | None = None) -> bytes:
                payload = {
                    "id": result["id"],
                    "object": "chat.completion.chunk",
                    "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
                }
                return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")

            async def stream_mock():
                yield chunk({"role": "assistant"})
                yield chunk({"content": text})
                yield b"data: [DONE]\n\n"

            return StreamingResponse(stream_mock(), media_type="text/event-stream")
        return JSONResponse(result)

    base_url = os.getenv("LLM_BASE_URL", "")
    api_key = os.getenv("LLM_API_KEY", "")
    if body.get("stream"):
        if not base_url:
            return error_response("LLM_BASE_URL is not configured", 503, "configuration_error")
        try:
            client = httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=10.0))
            response = await client.stream(
                "POST",
                upstream_url(base_url, "/v1/chat/completions"),
                headers=auth_headers(api_key),
                json=body,
            ).__aenter__()
        except httpx.TimeoutException:
            return error_response("Model upstream timed out", 504, "upstream_timeout")
        except httpx.HTTPError as exc:
            return error_response(f"Model upstream unavailable: {exc.__class__.__name__}", 502, "upstream_unavailable")

        if response.status_code >= 400:
            await client.aclose()
            return error_response(
                f"Model upstream returned HTTP {response.status_code}",
                response.status_code,
                upstream_error_type(response.status_code),
            )

        async def forward_stream():
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
            finally:
                await response.aclose()
                await client.aclose()

        return StreamingResponse(
            forward_stream(),
            status_code=response.status_code,
            media_type=response.headers.get("content-type", "text/event-stream"),
        )
    return await proxy_json("/v1/chat/completions", body, base_url, api_key)


@app.post("/v1/embeddings")
async def embeddings(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except ValueError:
        return error_response("Request body must be JSON", 400, "invalid_request_error")
    input_value = body.get("input") if isinstance(body, dict) else None
    if not isinstance(input_value, (str, list)) or not input_value:
        return error_response("input must be a non-empty string or array", 400, "invalid_request_error")

    if env_bool("MOCK_EMBEDDINGS") or env_bool("MOCK_MODE"):
        values = [input_value] if isinstance(input_value, str) else input_value
        dimension = int(os.getenv("MOCK_EMBEDDING_DIMENSION", "64"))
        return JSONResponse(
            {
                "object": "list",
                "data": [
                    {"object": "embedding", "index": index, "embedding": deterministic_embedding(str(value), dimension)}
                    for index, value in enumerate(values)
                ],
                "model": body.get("model") or os.getenv("EMBEDDING_MODEL", "mock-embedding"),
                "usage": {"prompt_tokens": 0, "total_tokens": 0},
            }
        )

    return await proxy_json(
        "/v1/embeddings",
        body,
        os.getenv("EMBEDDING_BASE_URL", ""),
        os.getenv("EMBEDDING_API_KEY", ""),
    )
