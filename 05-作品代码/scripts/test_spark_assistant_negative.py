#!/usr/bin/env python3
"""Run redacted Spark Assistant protocol-negative cases.

The cases contain no user data and never print response bodies. A case passes
only when the authenticated WebSocket returns a non-zero protocol error;
timeouts and successful answers remain failures for this negative suite.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.test_spark_assistant_ws import WebSocket, load_env, redact_config, signed_target


def case_payload(case: str, app_id: str) -> dict[str, object]:
    header: dict[str, object] = {"uid": "codex-negative-" + uuid.uuid4().hex[:12]}
    message: dict[str, object] = {"text": [{"role": "user", "content": "协议负向测试"}]}
    parameter: dict[str, object] = {"chat": {"temperature": 0.2, "max_tokens": 32}}
    if case != "missing-app-id":
        header["app_id"] = app_id
    if case == "missing-message":
        message = {}
    elif case == "invalid-role":
        message["text"] = [{"role": "invalid-role", "content": "协议负向测试"}]
    elif case == "invalid-temperature":
        parameter["chat"] = {"temperature": 999, "max_tokens": 32}
    return {"header": header, "parameter": parameter, "payload": {"message": message}}


def run_case(values: dict[str, str], case: str, timeout: float) -> tuple[bool, str]:
    endpoint, target, host_header = signed_target(values)
    client = WebSocket(endpoint, target, host_header, timeout)
    frames = 0
    codes: list[int] = []
    close_code: int | None = None
    try:
        handshake = client.connect()
        if handshake != 101:
            return False, f"handshake={handshake} frames=0 error_code=none"
        client.send_frame(0x1, json.dumps(case_payload(case, values["TEST_APP_ID"]), ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        if client.sock is not None:
            client.sock.settimeout(timeout)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and frames < 20:
            try:
                final, opcode, payload = client.recv_frame()
            except (socket.timeout, EOFError, OSError):
                break
            if opcode == 0x8:
                close_code = int.from_bytes(payload[:2], "big") if len(payload) >= 2 else None
                break
            if opcode == 0x9:
                client.send_frame(0xA, payload)
                continue
            if opcode != 0x1 or not final:
                continue
            frames += 1
            try:
                message = json.loads(payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            header = message.get("header") if isinstance(message, dict) else None
            code = header.get("code") if isinstance(header, dict) else None
            if isinstance(code, int):
                codes.append(code)
            if isinstance(header, dict) and code != 0:
                break
        close_code = client.close()
        error_code = next((code for code in codes if code != 0), None)
        passed = error_code is not None
        close_text = close_code if close_code is not None else "none"
        return passed, f"handshake=101 frames={frames} error_code={error_code if error_code is not None else 'none'} close_code={close_text}"
    finally:
        client.shutdown()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env.test.local")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()
    try:
        values = load_env(args.env_file)
        _, config_error = redact_config(values, args.env_file)
    except (OSError, ValueError) as error:
        print(f"config=FAIL type={type(error).__name__}")
        return 2
    if config_error:
        print(f"config=FAIL {config_error}")
        return 2

    failed = 0
    for case in ("missing-app-id", "missing-message", "invalid-role", "invalid-temperature"):
        try:
            passed, summary = run_case(values, case, args.timeout)
        except (OSError, ValueError, EOFError, socket.timeout, json.JSONDecodeError) as error:
            passed = False
            summary = f"result=error type={type(error).__name__}"
        print(f"case={case} result={'PASS' if passed else 'NOT_PASS'} {summary}")
        failed += 0 if passed else 1
    return 0 if failed == 0 else 6


if __name__ == "__main__":
    raise SystemExit(main())
