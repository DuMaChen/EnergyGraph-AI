#!/usr/bin/env python3
"""Exercise the Adapter against a local HTTP Workflow fixture.

This is deliberately not a fake ``httpx`` client.  The fixture uses a real
loopback socket so request serialization, Authorization, SSE parsing, source
validation and the provider finish frame are tested together without needing
the team's private Xingchen credentials.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MOCK_WORKFLOW_MODE", "false")
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "http-fixture-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


class WorkflowFixtureHandler(BaseHTTPRequestHandler):
    """Return the minimum official-shaped streaming response used by Adapter."""

    requests: list[dict[str, object]] = []

    def log_message(self, *_args: object) -> None:
        # The test must stay quiet: request bodies could contain course text.
        return

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        self.requests.append({"headers": dict(self.headers), "body": body})
        assert self.headers.get("Authorization") == "Bearer fixture-key:fixture-secret"
        assert body["flow_id"] == "flow-fixture"
        assert body["uid"] == "u_http_fixture"
        assert body["stream"] is True

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        frames = [
            {"code": 0, "choices": [{"delta": {"content": "课程答案 "}}]},
            {"code": 0, "choices": [{"delta": {"content": "[来源文件：3.4 储能变流器拓扑及并网控制.pdf；章节：第3章 电力储能系统的组成及工作原理；页码：1]"}}]},
            {"code": 0, "choices": [{"delta": {}, "finish_reason": "stop"}]},
        ]
        for frame in frames:
            self.wfile.write(f"data: {json.dumps(frame, ensure_ascii=False)}\n\n".encode("utf-8"))
            self.wfile.flush()


async def collect_events(stream_function: object, identity: object) -> list[dict[str, object]]:
    """Collect the adapter's async event contract while keeping the fixture small."""
    return [
        event
        async for event in stream_function(  # type: ignore[misc]
            {"AGENT_USER_INPUT": "解释储能变流器", "AGENT_MODE": "qa"},
            identity,
            "http-fixture-request",
            "flow-fixture",
        )
    ]


def main() -> None:
    sys.path.insert(0, str(ROOT / "agent-adapter"))
    from app import main as adapter  # noqa: E402

    server = ThreadingHTTPServer(("127.0.0.1", 0), WorkflowFixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        adapter.MANIFEST = {
            "files": [
                {
                    "source_file": "3.4 储能变流器拓扑及并网控制.pdf",
                    "chapter": "第3章 电力储能系统的组成及工作原理",
                    "normalized_file": "chapter-3-3.4-.pdf",
                    "chapter_id": 3,
                    "page_count": 38,
                    "sha256": "fixture-sha256",
                }
            ]
        }
        os.environ.update(
            {
                "MOCK_WORKFLOW_MODE": "false",
                "XINGCHEN_FLOW_ID": "env-flow-should-not-win",
                "XINGCHEN_API_KEY": "fixture-key",
                "XINGCHEN_API_SECRET": "fixture-secret",
                "XINGCHEN_WORKFLOW_URL": f"http://127.0.0.1:{server.server_port}/workflow/v1/chat/completions",
            }
        )
        identity = adapter.Identity("u_http_fixture", "student", 1)
        events = asyncio.run(collect_events(adapter.xingchen_stream, identity))
        assert [event["event"] for event in events] == ["token", "token", "source", "done"]
        assert events[2]["data"]["file"] == "3.4 储能变流器拓扑及并网控制.pdf"
        assert events[2]["data"]["page"] == 1
        assert len(WorkflowFixtureHandler.requests) == 1
        print("XINGCHEN_HTTP_FIXTURE_OK")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
