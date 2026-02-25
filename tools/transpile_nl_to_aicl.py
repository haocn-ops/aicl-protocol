#!/usr/bin/env python3
"""Rule-based natural language to AICL draft transpiler (v0.1)."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import uuid


INTENT_HINTS = [
    ("verify", "VERIFY"),
    ("validate", "VALIDATE"),
    ("check", "VERIFY"),
    ("plan", "PLAN"),
    ("summarize", "SUMMARIZE"),
    ("report", "REPORT"),
    ("delegate", "DELEGATE"),
    ("negotiate", "NEGOTIATE"),
    ("ask", "ASK"),
]


def infer_intent(text: str) -> str:
    lowered = text.lower()
    for token, intent in INTENT_HINTS:
        if token in lowered:
            return intent
    return "ASK"


def infer_object(text: str) -> str:
    cleaned = re.sub(r"\s+", "_", text.strip().lower())
    cleaned = re.sub(r"[^a-z0-9_/-]", "", cleaned)
    return f"task/{cleaned[:64] or 'unnamed'}"


def infer_deadline(hours: int = 24) -> str:
    due = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=hours)
    return due.replace(microsecond=0).isoformat()


def transpile(text: str, default_conf: float = 0.70) -> str:
    intent = infer_intent(text)
    obj = infer_object(text)
    trace = f"trc_{uuid.uuid4().hex[:10]}"
    deadline = infer_deadline()
    return "\n".join(
        [
            "MSG{",
            f"I:{intent}",
            f"O:{obj}",
            f"C:deadline={deadline};policy=P1",
            f"K:[user_request=\"{text.strip()}\"]",
            "U:[missing_context]",
            "Q:[confirm_scope?]",
            "X:deliver=markdown",
            f"S:conf={default_conf:.2f};ver=1.0;trace={trace}",
            "}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Transpile natural language into AICL draft.")
    parser.add_argument("text", help="Natural language request")
    parser.add_argument("--conf", type=float, default=0.70, help="Default confidence in S.conf")
    args = parser.parse_args()
    print(transpile(args.text, default_conf=args.conf))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

