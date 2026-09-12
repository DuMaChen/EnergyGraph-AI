#!/usr/bin/env python3
"""Exercise the graph, textbook locator, and scenario contract as one case."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "acceptance/test-fixtures/scenarios.json"
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("MOCK_WORKFLOW_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "graph-scenario-fixture-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


def data(response: object, expected: int) -> dict:
    assert response.status_code == expected, (response.status_code, response.text)
    return response.json()["data"]


def main() -> None:
    with tempfile.NamedTemporaryFile(prefix="graph-scenario-", suffix=".db") as db_file:
        os.environ["COURSE_DB"] = db_file.name
        import sys

        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        student = {"x-dev-role": "student", "x-dev-user": "graph-student"}
        other_student = {"x-dev-role": "student", "x-dev-user": "other-student"}
        scenarios = json.loads(FIXTURE.read_text(encoding="utf-8"))
        assert {item["key"] for item in scenarios["scenarios"]} == {"grid-dispatch", "battery-fault"}

        chapters = data(client.get("/api/knowledge-graph/chapters", headers=student), 200)
        assert chapters["total"] == 6
        node = data(client.get("/api/knowledge-graph/nodes/kp-3-4", headers=student), 200)
        assert node["name"].startswith("3.4") and node["resources"]
        path = data(
            client.get("/api/knowledge-graph/paths?from=kp-3-1&to=kp-3-4", headers=student),
            200,
        )
        assert path["path"][0] == "kp-3-1" and path["path"][-1] == "kp-3-4"
        resource = node["resources"][0]
        located = data(client.get(f"/api/textbook/resources/{resource['id']}?page=1", headers=student), 200)
        assert "resource.php" in located["locator"] and located["page"] == 1
        page = data(client.get(f"/api/textbook/resources/{resource['id']}/pages/1", headers=student), 200)
        assert page["resource"]["id"] == resource["id"]

        for index, scenario_key in enumerate(("grid-dispatch", "battery-fault"), start=1):
            start_key = f"case006-start-{index}"
            started = data(
                client.post(
                    "/api/scenarios/start",
                    headers={**student, "idempotency-key": start_key},
                    json={"scenario_key": scenario_key},
                ),
                201,
            )
            session_id = started["session_id"]
            turn_key = f"case006-turn-{index}"
            turn_body = {"turn_no": 1, "text": "请根据当前模拟条件给出排查或调度思路。"}
            turn = data(
                client.post(
                    f"/api/scenarios/{session_id}/turn",
                    headers={**student, "idempotency-key": turn_key},
                    json=turn_body,
                ),
                200,
            )
            assert turn["status"] == "completed" and turn["assistant_text"]
            assert turn["evidence"]
            retry = data(
                client.post(
                    f"/api/scenarios/{session_id}/turn",
                    headers={**student, "idempotency-key": turn_key},
                    json=turn_body,
                ),
                200,
            )
            assert retry["assistant_text"] == turn["assistant_text"]
            assert client.post(
                f"/api/scenarios/{session_id}/turn",
                headers={**other_student, "idempotency-key": f"case006-other-{index}"},
                json=turn_body,
            ).status_code == 404
            ended = data(
                client.post(
                    f"/api/scenarios/{session_id}/end",
                    headers={**student, "idempotency-key": f"case006-end-{index}"},
                    json={"state": "completed"},
                ),
                200,
            )
            assert ended["state"] == "completed" and ended["turn_count"] == 1
            assert client.post(
                f"/api/scenarios/{session_id}/turn",
                headers={**student, "idempotency-key": f"case006-after-end-{index}"},
                json={"turn_no": 2, "text": "继续。"},
            ).status_code == 409

    print("CASE006_GRAPH_TEXTBOOK_SCENARIO_OK")


if __name__ == "__main__":
    main()
