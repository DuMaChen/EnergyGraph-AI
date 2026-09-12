#!/usr/bin/env python3
"""Test the Spark Assistant signing and WebSocket framing contract offline.

This suite never opens a socket and uses fixture credentials only to prove
that URL signing does not expose raw secrets. Remote negative cases remain a
separate acceptance layer and must be run only with the configured test
endpoint.
"""

from __future__ import annotations

import base64
import os
import struct
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from scripts.test_spark_assistant_auth_negative import tampered_target
from scripts.test_spark_assistant_ws import WebSocket, redact_config, signed_target


class MemorySocket:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def recv(self, size: int) -> bytes:
        chunk, self.payload = self.payload[:size], self.payload[size:]
        return chunk


def server_frame(payload: bytes) -> bytes:
    if len(payload) >= 126:
        raise ValueError("fixture_payload_too_large")
    return bytes((0x81, len(payload))) + payload


class SparkAssistantContractTests(unittest.TestCase):
    def fixture_values(self) -> dict[str, str]:
        return {
            "TEST_API_BASE_URL": "wss://spark-openapi.example.test/v1/assistants/assistant-123",
            "TEST_APP_ID": "fixture-app",
            "TEST_API_KEY": "fixture-key",
            "TEST_API_SECRET": "fixture-secret",
        }

    def test_missing_config_is_redacted(self) -> None:
        with tempfile.NamedTemporaryFile() as handle:
            os.chmod(handle.name, 0o600)
            _, error = redact_config({"TEST_API_KEY": "fixture-secret"}, Path(handle.name))
        self.assertIsNotNone(error)
        self.assertIn("missing=TEST_API_BASE_URL", error or "")
        self.assertNotIn("fixture-secret", error or "")

    def test_invalid_endpoint_shapes_are_rejected(self) -> None:
        values = self.fixture_values()
        for endpoint, expected in (
            ("ws(s)://spark-openapi.example.test/v1/assistants/id", "invalid_websocket_endpoint"),
            ("wss://spark-openapi.example.test/assistants/id", "invalid_assistant_path"),
            ("wss://user:pass@spark-openapi.example.test/v1/assistants/id", "endpoint_userinfo_not_allowed"),
            ("wss://spark-openapi.example.invalid/v1/assistants/id", "placeholder_endpoint"),
        ):
            with self.subTest(expected=expected):
                values["TEST_API_BASE_URL"] = endpoint
                with self.assertRaisesRegex(ValueError, expected):
                    signed_target(values)

    def test_signed_target_contains_only_expected_auth_query(self) -> None:
        values = self.fixture_values()
        endpoint, target, host = signed_target(values)
        self.assertEqual(endpoint.scheme, "wss")
        self.assertEqual(host, "spark-openapi.example.test")
        self.assertIn("authorization=", target)
        self.assertIn("date=", target)
        self.assertIn("host=", target)
        self.assertNotIn(values["TEST_API_KEY"], target)
        self.assertNotIn(values["TEST_API_SECRET"], target)

    def test_preexisting_auth_query_is_rejected(self) -> None:
        values = self.fixture_values()
        values["TEST_API_BASE_URL"] += "?authorization=caller-supplied"
        with self.assertRaisesRegex(ValueError, "preexisting_auth_query"):
            signed_target(values)

    def test_negative_cases_mutate_auth_material_offline(self) -> None:
        values = self.fixture_values()
        _, valid_target, _ = signed_target(values)
        valid_query = dict(parse_qsl(urlsplit(valid_target).query, keep_blank_values=True))
        for case in ("wrong-app-id", "wrong-api-key", "wrong-secret", "tampered-date"):
            with self.subTest(case=case):
                _, target, _ = tampered_target(values, case)
                query = dict(parse_qsl(urlsplit(target).query, keep_blank_values=True))
                self.assertIn("authorization", query)
                if case == "wrong-app-id":
                    self.assertEqual(query, valid_query)
                elif case == "wrong-api-key":
                    self.assertNotEqual(query, valid_query)
                    decoded = base64.b64decode(query["authorization"]).decode("utf-8")
                    self.assertIn('api_key="invalid-test-api-key"', decoded)
                elif case == "wrong-secret":
                    self.assertNotEqual(query, valid_query)
                    self.assertNotEqual(query["authorization"], valid_query["authorization"])
                else:
                    self.assertNotEqual(query, valid_query)
                    self.assertNotEqual(query["date"], valid_query["date"])

    def test_unmasked_server_frame_is_decoded(self) -> None:
        payload = b'{"header":{"code":0},"payload":{"choices":{"status":2}}}'
        client = WebSocket(self.fixture_endpoint(), "/v1/assistants/id", "spark-openapi.example.test", 1)
        client.sock = MemorySocket(server_frame(payload))  # type: ignore[assignment]
        final, opcode, received = client.recv_frame()
        self.assertTrue(final)
        self.assertEqual(opcode, 1)
        self.assertEqual(received, payload)

    def test_masked_frame_is_decoded(self) -> None:
        payload = b"fixture"
        mask = b"abcd"
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        frame = bytes((0x81, 0x80 | len(payload))) + mask + masked
        client = WebSocket(self.fixture_endpoint(), "/v1/assistants/id", "spark-openapi.example.test", 1)
        client.sock = MemorySocket(frame)  # type: ignore[assignment]
        _, opcode, received = client.recv_frame()
        self.assertEqual(opcode, 1)
        self.assertEqual(received, payload)

    @staticmethod
    def fixture_endpoint():
        from urllib.parse import urlsplit

        return urlsplit("wss://spark-openapi.example.test/v1/assistants/id")


if __name__ == "__main__":
    unittest.main()
