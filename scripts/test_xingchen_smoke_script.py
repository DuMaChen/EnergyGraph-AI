#!/usr/bin/env python3
"""Run the real-provider smoke shell script against a local protocol fixture.

The fixture deliberately uses a real loopback HTTP server. It verifies the
shell script's request shape and strict response checks without requiring a
private Xingchen credential or sending course data to an external service.
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SmokeHandler(BaseHTTPRequestHandler):
    requests = 0

    def log_message(self, *_args: object) -> None:
        # Keep request bodies and provider-like output out of test logs.
        return

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        assert self.headers.get("Authorization") == "Bearer fixture-key:fixture-secret"
        assert payload["flow_id"] == "fixture-flow"
        SmokeHandler.requests += 1

        self.send_response(200)
        if payload.get("stream"):
            self.send_header("Content-Type", "text/event-stream")
        else:
            self.send_header("Content-Type", "application/json")
        self.end_headers()

        if not payload.get("stream"):
            body = {
                "code": 0,
                "choices": [{"message": {"content": "非流式夹具答案"}}],
            }
            self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))
            return

        frames = [
            {"code": 0, "choices": [{"delta": {"content": "流式夹具答案"}}]},
            {"code": 0, "choices": [{"delta": {}, "finish_reason": "stop"}]},
        ]
        for frame in frames:
            self.wfile.write(f"data: {json.dumps(frame, ensure_ascii=False)}\n\n".encode("utf-8"))
            self.wfile.flush()


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), SmokeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        environment = {
            **os.environ,
            "XINGCHEN_WORKFLOW_URL": f"http://127.0.0.1:{server.server_port}/workflow",
            "XINGCHEN_FLOW_ID": "fixture-flow",
            "XINGCHEN_API_KEY": "fixture-key",
            "XINGCHEN_API_SECRET": "fixture-secret",
            "XINGCHEN_TIMEOUT_SECONDS": "5",
        }
        result = subprocess.run(
            ["bash", str(ROOT / "scripts/xingchen_smoke.sh")],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr or result.stdout
        assert "XFYUN_REAL_SMOKE success=5/5" in result.stdout
        assert SmokeHandler.requests == 6, SmokeHandler.requests
        print("XINGCHEN_SMOKE_SCRIPT_FIXTURE_OK")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
