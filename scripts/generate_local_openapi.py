#!/usr/bin/env python3
"""Export the current Adapter route schema as an explicitly local test contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "agent-adapter") not in sys.path:
    sys.path.insert(0, str(ROOT / "agent-adapter"))

from app.main import app


output = ROOT / "openapi.test.json"
schema = app.openapi()
schema["info"]["title"] = "EnergyGraph-AI Local Isolated Adapter Contract"
schema["info"]["description"] = (
    "Generated from the local Adapter application. This is not a formal Moodle or production API contract."
)
schema["x-environment"] = "local-isolated-adapter"
schema["x-formal-external-contract"] = False
output.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"LOCAL_OPENAPI_EXPORTED paths={len(schema.get('paths', {}))} output={output.name}")
