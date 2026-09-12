#!/usr/bin/env python3
"""Verify Spark Assistant rejects invalid authentication before a business frame."""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.test_spark_assistant_ws import WebSocket, load_env, redact_config, signed_target


def tampered_target(values: dict[str, str], case: str) -> tuple[object, str, str]:
    candidate = dict(values)
    if case == "wrong-app-id":
        return signed_target(candidate)
    if case == "wrong-api-key":
        candidate["TEST_API_KEY"] = "invalid-test-api-key"
        return signed_target(candidate)
    if case == "wrong-secret":
        candidate["TEST_API_SECRET"] = "invalid-test-api-secret"
        return signed_target(candidate)
    endpoint, target, host = signed_target(candidate)
    parts = urlsplit(target)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["date"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    return endpoint, urlunsplit(("", "", parts.path, urlencode(query), "")), host


def run_case(values: dict[str, str], case: str, timeout: float) -> tuple[bool, str]:
    endpoint, target, host = tampered_target(values, case)
    client = WebSocket(endpoint, target, host, timeout)  # type: ignore[arg-type]
    try:
        status = client.connect()
        if status != 101:
            return True, f"handshake={status} business_frame_sent=no"
        request = {
            "header": {
                "app_id": "00000000" if case == "wrong-app-id" else values["TEST_APP_ID"],
                "uid": "codex-auth-negative",
            },
            "parameter": {"chat": {"temperature": 0.2, "max_tokens": 32}},
            "payload": {"message": {"text": [{"role": "user", "content": "认证负向测试"}]}},
        }
        client.send_frame(0x1, json.dumps(request, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        if client.sock is not None:
            client.sock.settimeout(timeout)
        deadline = time.monotonic() + timeout
        frames = 0
        error_code: int | None = None
        final_seen = False
        final_code: int | None = None
        while time.monotonic() < deadline and frames < 10:
            final, opcode, payload = client.recv_frame()
            if opcode == 0x8:
                break
            if opcode == 0x9:
                client.send_frame(0xA, payload)
                continue
            if opcode != 0x1 or not final:
                continue
            frames += 1
            try:
                response = json.loads(payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            header = response.get("header") if isinstance(response, dict) else None
            code = header.get("code") if isinstance(header, dict) else None
            if isinstance(code, int) and code != 0:
                error_code = code
                break
            choices = response.get("payload", {}).get("choices", {}) if isinstance(response, dict) else {}
            if isinstance(choices, dict) and choices.get("status") == 2:
                final_seen = True
                final_code = code if isinstance(code, int) else None
                break
        client.close()
        passed = error_code is not None
        result_code = error_code if error_code is not None else final_code
        return passed, f"handshake=101 business_frame_sent=yes frames={frames} error_code={result_code if result_code is not None else 'none'} final_seen={'yes' if final_seen else 'no'}"
    except (OSError, EOFError, ValueError, socket.timeout) as error:
        return False, f"result=error type={type(error).__name__}"
    finally:
        client.shutdown()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env.test.local")
    parser.add_argument("--timeout", type=float, default=10.0)
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
    for case in ("wrong-app-id", "wrong-api-key", "wrong-secret", "tampered-date"):
        passed, summary = run_case(values, case, args.timeout)
        print(f"case={case} result={'PASS' if passed else 'NOT_PASS'} {summary}")
        failed += 0 if passed else 1
    return 0 if failed == 0 else 6


if __name__ == "__main__":
    raise SystemExit(main())
