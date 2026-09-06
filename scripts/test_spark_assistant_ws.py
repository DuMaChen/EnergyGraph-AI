#!/usr/bin/env python3
"""Run a redacted positive Spark Assistant WebSocket smoke test.

This client intentionally uses only the Python standard library so the test
does not depend on a package installation in a restricted environment. It
loads credentials from an ignored local env file, never prints the signed URL
or response text, and exits non-zero unless the complete response and close
handshake are valid.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import socket
import ssl
import struct
import time
import urllib.parse
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("TEST_API_BASE_URL", "TEST_APP_ID", "TEST_API_KEY", "TEST_API_SECRET")
QUESTION = "请只回复“测试成功”，不要补充其他内容。"


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def redact_config(values: dict[str, str], env_path: Path) -> tuple[dict[str, str], str | None]:
    missing = [name for name in REQUIRED if not values.get(name)]
    if missing:
        return values, "missing=" + ",".join(missing)
    if env_path.name == ".env.test.local" and env_path.stat().st_mode & 0o777 != 0o600:
        return values, "local_env_permission_not_600"
    return values, None


def signed_target(values: dict[str, str]) -> tuple[urllib.parse.SplitResult, str, str]:
    endpoint = urllib.parse.urlsplit(values["TEST_API_BASE_URL"])
    if endpoint.scheme not in {"ws", "wss"} or not endpoint.hostname:
        raise ValueError("invalid_websocket_endpoint")
    if endpoint.username or endpoint.password:
        raise ValueError("endpoint_userinfo_not_allowed")
    if not endpoint.path.startswith("/v1/assistants/") or endpoint.path == "/v1/assistants/":
        raise ValueError("invalid_assistant_path")
    if ".invalid" in endpoint.hostname or "ws(s)" in values["TEST_API_BASE_URL"]:
        raise ValueError("placeholder_endpoint")
    existing_query = urllib.parse.parse_qsl(endpoint.query, keep_blank_values=True)
    if {key for key, _ in existing_query} & {"authorization", "date", "host"}:
        raise ValueError("preexisting_auth_query")
    port = endpoint.port or (443 if endpoint.scheme == "wss" else 80)
    host_header = endpoint.hostname if port in {80, 443} else f"{endpoint.hostname}:{port}"
    date = dt.datetime.now(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    signature_origin = f"host: {host_header}\ndate: {date}\nGET {endpoint.path} HTTP/1.1"
    signature = base64.b64encode(
        hmac.new(values["TEST_API_SECRET"].encode(), signature_origin.encode(), hashlib.sha256).digest()
    ).decode()
    authorization_origin = (
        f'api_key="{values["TEST_API_KEY"]}", '
        f'algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    )
    query = existing_query + [
        ("authorization", base64.b64encode(authorization_origin.encode()).decode()),
        ("date", date),
        ("host", host_header),
    ]
    target = endpoint.path + "?" + urllib.parse.urlencode(query)
    return endpoint, target, host_header


class WebSocket:
    def __init__(self, endpoint: urllib.parse.SplitResult, target: str, host_header: str, timeout: float) -> None:
        self.endpoint = endpoint
        self.target = target
        self.host_header = host_header
        self.timeout = timeout
        self.sock: socket.socket | None = None

    def connect(self) -> int:
        port = self.endpoint.port or (443 if self.endpoint.scheme == "wss" else 80)
        raw = socket.create_connection((self.endpoint.hostname, port), timeout=self.timeout)
        if self.endpoint.scheme == "wss":
            self.sock = ssl.create_default_context().wrap_socket(raw, server_hostname=self.endpoint.hostname)
        else:
            self.sock = raw
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            f"GET {self.target} HTTP/1.1\r\n"
            f"Host: {self.host_header}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii")
        self.sock.sendall(request)
        response = bytearray()
        while b"\r\n\r\n" not in response and len(response) < 65536:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            response.extend(chunk)
        first_line = bytes(response).split(b"\r\n", 1)[0].decode("ascii", "replace")
        parts = first_line.split()
        return int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0

    def send_frame(self, opcode: int, payload: bytes = b"") -> None:
        if self.sock is None:
            raise RuntimeError("socket_not_connected")
        mask = os.urandom(4)
        size = len(payload)
        if size < 126:
            header = bytes((0x80 | opcode, 0x80 | size))
        elif size < 65536:
            header = bytes((0x80 | opcode, 0x80 | 126)) + struct.pack("!H", size)
        else:
            header = bytes((0x80 | opcode, 0x80 | 127)) + struct.pack("!Q", size)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(header + mask + masked)

    def recv_exact(self, size: int) -> bytes:
        if self.sock is None:
            raise RuntimeError("socket_not_connected")
        data = bytearray()
        while len(data) < size:
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                raise EOFError("peer_closed")
            data.extend(chunk)
        return bytes(data)

    def recv_frame(self) -> tuple[bool, int, bytes]:
        first, second = self.recv_exact(2)
        opcode = first & 0x0F
        final = bool(first & 0x80)
        masked = bool(second & 0x80)
        size = second & 0x7F
        if size == 126:
            size = struct.unpack("!H", self.recv_exact(2))[0]
        elif size == 127:
            size = struct.unpack("!Q", self.recv_exact(8))[0]
        mask = self.recv_exact(4) if masked else None
        payload = self.recv_exact(size) if size else b""
        if mask:
            payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        return final, opcode, payload

    def close(self) -> int | None:
        if self.sock is None:
            return None
        peer_code: int | None = None
        try:
            self.send_frame(0x8, struct.pack("!H", 1000))
            self.sock.settimeout(3)
            while peer_code is None:
                final, opcode, payload = self.recv_frame()
                del final
                if opcode == 0x8:
                    peer_code = struct.unpack("!H", payload[:2])[0] if len(payload) >= 2 else None
                    break
                if opcode == 0x9:
                    self.send_frame(0xA, payload)
        except (socket.timeout, EOFError, OSError):
            return peer_code
        return peer_code

    def shutdown(self) -> None:
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None


def run(values: dict[str, str], timeout: float) -> int:
    endpoint, target, host_header = signed_target(values)
    client = WebSocket(endpoint, target, host_header, timeout)
    frames = 0
    header_codes: list[int] = []
    header_statuses: list[int] = []
    choice_statuses: list[int] = []
    seqs: list[int] = []
    sid_present = False
    text_array_valid = True
    assistant_content_present = False
    final_seen = False
    try:
        handshake_status = client.connect()
        if handshake_status != 101:
            print(f"handshake=FAIL status={handshake_status}")
            return 3
        request = {
            "header": {"app_id": values["TEST_APP_ID"], "uid": "codex-test-" + uuid.uuid4().hex[:12]},
            "parameter": {"chat": {"temperature": 0.2, "max_tokens": 256}},
            "payload": {"message": {"text": [{"role": "user", "content": QUESTION}]}},
        }
        client.send_frame(0x1, json.dumps(request, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        client.sock.settimeout(timeout)  # type: ignore[union-attr]
        assembled = bytearray()
        fragmented = False
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and frames < 100 and not final_seen:
            final, opcode, payload = client.recv_frame()
            if opcode == 0x8:
                break
            if opcode == 0x9:
                client.send_frame(0xA, payload)
                continue
            if opcode == 0xA:
                continue
            if opcode == 0x1:
                assembled = bytearray(payload)
                fragmented = True
            elif opcode == 0x0 and fragmented:
                assembled.extend(payload)
            else:
                continue
            if not final:
                continue
            frames += 1
            message = json.loads(assembled.decode("utf-8"))
            header = message.get("header", {})
            choices = message.get("payload", {}).get("choices", {})
            if not isinstance(header, dict) or not isinstance(choices, dict):
                text_array_valid = False
                break
            if isinstance(header.get("code"), int):
                header_codes.append(header["code"])
            else:
                text_array_valid = False
            if isinstance(header.get("status"), int):
                header_statuses.append(header["status"])
            else:
                text_array_valid = False
            sid_present = sid_present or bool(header.get("sid"))
            if isinstance(choices.get("status"), int):
                choice_statuses.append(choices["status"])
            else:
                text_array_valid = False
            if isinstance(choices.get("seq"), int):
                seqs.append(choices["seq"])
            else:
                text_array_valid = False
            text = choices.get("text")
            if not isinstance(text, list):
                text_array_valid = False
            else:
                for item in text:
                    if not isinstance(item, dict) or item.get("role") != "assistant" or not isinstance(item.get("content"), str):
                        text_array_valid = False
                    elif item["content"].strip():
                        assistant_content_present = True
            final_seen = choices.get("status") == 2
            assembled.clear()
            fragmented = False
        close_code = client.close()
        seq_valid = bool(seqs) and seqs[0] == 0 and all(left < right for left, right in zip(seqs, seqs[1:]))
        header_final = bool(header_statuses) and header_statuses[-1] == 2
        choices_final = bool(choice_statuses) and choice_statuses[-1] == 2
        all_codes_zero = bool(header_codes) and all(code == 0 for code in header_codes)
        close_normal = close_code in {1000, 1001}
        print(
            "handshake=PASS "
            f"header_code={header_codes[0] if header_codes else 'missing'} "
            f"sid_present={'yes' if sid_present else 'no'} "
            f"frames={frames} "
            f"text_array_valid={'yes' if text_array_valid else 'no'} "
            f"assistant_role_content={'yes' if assistant_content_present else 'no'} "
            f"seq_valid={'yes' if seq_valid else 'no'} "
            f"header_final_status={'yes' if header_final else 'no'} "
            f"choice_final_status={'yes' if choices_final else 'no'} "
            f"close_code={close_code if close_code is not None else 'not_received'} "
            f"close_normal={'yes' if close_normal else 'no'}"
        )
        return 0 if all((all_codes_zero, sid_present, text_array_valid, assistant_content_present, seq_valid, final_seen, header_final, choices_final, close_normal)) else 6
    except socket.timeout:
        print(f"handshake=PASS result=timeout frames={frames}")
        return 4
    except (OSError, EOFError, ValueError, json.JSONDecodeError) as error:
        print(f"handshake={'PASS' if frames or client.sock else 'FAIL'} result=error type={type(error).__name__} frames={frames}")
        return 5
    finally:
        client.shutdown()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env.test.local")
    parser.add_argument("--timeout", type=float, default=30.0)
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
    try:
        return run(values, args.timeout)
    except ValueError as error:
        print(f"config=FAIL type={error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
