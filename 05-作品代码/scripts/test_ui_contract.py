#!/usr/bin/env python3
"""Check static UI invariants that do not require a browser connection."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "agent-ui/index.html").read_text(encoding="utf-8")


def require(fragment: str, message: str) -> None:
    assert fragment in HTML, message


def main() -> None:
    require('<meta name="viewport" content="width=device-width, initial-scale=1">', "viewport meta missing")
    require(".kb-grid, .teacher-grid { grid-template-columns: 1fr; }", "mobile teacher layout missing")
    require(".teacher-grid button { width: 100%; }", "mobile teacher action sizing missing")
    require("white-space: normal", "AI badge must be allowed to wrap")
    require("function operationKey(scope, signature)", "operation key helper missing")
    require("randomOperationToken", "secure-context random fallback missing")
    require("AI 生成内容，请核验课程来源", "AI disclosure missing")

    # A timestamp in a write header creates a new business operation on every
    # retry. The UI must derive all such keys from operationKey or a stable id.
    assert all("Date.now()" not in line for line in HTML.splitlines() if "Idempotency-Key" in line), "timestamp-based idempotency key remains"
    assert "innerHTML" not in HTML, "UI must render untrusted content without innerHTML"
    assert "eval(" not in HTML, "dynamic code execution is forbidden"
    print("UI_CONTRACT_OK")


if __name__ == "__main__":
    main()
