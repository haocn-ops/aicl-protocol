#!/usr/bin/env python3
"""AICL v1.0 validator.

Base checks:
- required fields (I, O, S)
- intent membership
- S field contains conf/ver/trace
- conf range is 0..1

Strict checks (enabled via --strict):
- canonical field order
- unknown field detection
- high-risk COMMIT requires R and H
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


INTENTS = {
    "ASK",
    "INFORM",
    "PLAN",
    "ACT",
    "VERIFY",
    "NEGOTIATE",
    "DELEGATE",
    "ACCEPT",
    "REJECT",
    "ESCALATE",
    "SUMMARIZE",
    "COMPARE",
    "ESTIMATE",
    "PRIORITIZE",
    "SCHEDULE",
    "BLOCK",
    "UNBLOCK",
    "REPLAN",
    "CANCEL",
    "PAUSE",
    "RESUME",
    "COMMIT",
    "ROLLBACK",
    "AUDIT",
    "TRACE",
    "CITE",
    "CLARIFY",
    "CONFIRM",
    "DISPUTE",
    "RESOLVE",
    "SPLIT",
    "MERGE",
    "ROUTE",
    "HANDOFF",
    "MONITOR",
    "ALERT",
    "REPORT",
    "DIAGNOSE",
    "FIX",
    "TEST",
    "VALIDATE",
    "SANITIZE",
    "FILTER",
    "TRANSFORM",
    "RETRIEVE",
    "SYNTHESIZE",
    "CRITIQUE",
    "JUSTIFY",
    "PREDICT",
    "CLOSE",
}

KNOWN_FIELDS = ["A", "I", "O", "T", "G", "C", "K", "U", "P", "R", "Q", "D", "V", "M", "H", "X", "S"]
KNOWN_FIELD_SET = set(KNOWN_FIELDS)


@dataclass
class ValidationError:
    code: str
    message: str


def parse_fields(text: str) -> tuple[dict[str, str], list[str]]:
    match = re.search(r"MSG\s*\{(?P<body>.*)\}\s*$", text, flags=re.DOTALL)
    if not match:
        return {}, []
    body = match.group("body")
    fields: dict[str, str] = {}
    order: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        key = k.strip()
        fields[key] = v.strip()
        order.append(key)
    return fields, order


def parse_s_object(s_value: str) -> dict[str, str]:
    # Accept both:
    # S:{conf=0.8,ver=1.0,trace=t1}
    # S:conf=0.8;ver=1.0;trace=t1
    raw = s_value.strip()
    if raw.startswith("{") and raw.endswith("}"):
        raw = raw[1:-1]
    raw = raw.replace(";", ",")
    data: dict[str, str] = {}
    for part in raw.split(","):
        part = part.strip()
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        data[k.strip()] = v.strip()
    return data


def _is_high_risk_commit(fields: dict[str, str]) -> bool:
    return fields.get("I") == "COMMIT"


def _field_order_valid(order: list[str]) -> bool:
    # Canonical order means fields should appear in the same relative order.
    ranks = [KNOWN_FIELDS.index(k) for k in order if k in KNOWN_FIELD_SET]
    return ranks == sorted(ranks)


def validate_text(text: str, strict: bool = False) -> list[ValidationError]:
    errs: list[ValidationError] = []
    fields, order = parse_fields(text)
    if not fields:
        return [ValidationError("E001_MISSING_REQUIRED_FIELD", "Input is not a valid MSG{...} block.")]

    for required in ("I", "O", "S"):
        if required not in fields:
            errs.append(ValidationError("E001_MISSING_REQUIRED_FIELD", f"Missing required field: {required}"))

    intent = fields.get("I")
    if intent and intent not in INTENTS:
        errs.append(ValidationError("E002_INVALID_INTENT", f"Unknown intent: {intent}"))

    if "S" in fields:
        s_data = parse_s_object(fields["S"])
        for key in ("conf", "ver", "trace"):
            if key not in s_data:
                errs.append(ValidationError("E001_MISSING_REQUIRED_FIELD", f"S missing key: {key}"))
        if "conf" in s_data:
            try:
                conf = float(s_data["conf"])
                if conf < 0.0 or conf > 1.0:
                    errs.append(ValidationError("E003_INVALID_CONFIDENCE_RANGE", f"S.conf out of range: {conf}"))
            except ValueError:
                errs.append(ValidationError("E003_INVALID_CONFIDENCE_RANGE", f"S.conf is not a number: {s_data['conf']}"))

    if strict:
        unknown = [k for k in order if k not in KNOWN_FIELD_SET]
        if unknown:
            errs.append(ValidationError("E002_INVALID_INTENT", f"Unknown field(s): {', '.join(unknown)}"))
        if not _field_order_valid(order):
            errs.append(ValidationError("E004_CONSTRAINT_CONFLICT", "Fields are not in canonical order."))
        if _is_high_risk_commit(fields):
            if "R" not in fields:
                errs.append(ValidationError("E001_MISSING_REQUIRED_FIELD", "COMMIT in strict mode requires R field."))
            if "H" not in fields:
                errs.append(ValidationError("E205_HITL_REQUIRED_BUT_SKIPPED", "COMMIT in strict mode requires H field."))

    return errs


def validate_file(path: Path, strict: bool = False) -> int:
    text = path.read_text(encoding="utf-8")
    errs = validate_text(text, strict=strict)
    if errs:
        print(f"[FAIL] {path}")
        for err in errs:
            print(f"  - {err.code}: {err.message}")
        return 1
    print(f"[OK]   {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AICL message files.")
    parser.add_argument("paths", nargs="+", help="AICL files or directories")
    parser.add_argument("--strict", action="store_true", help="Enable strict checks.")
    args = parser.parse_args()

    rc = 0
    all_files: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            all_files.extend(sorted(path.rglob("*.aicl")))
        else:
            all_files.append(path)

    if not all_files:
        print("No .aicl files found.")
        return 1

    for file_path in all_files:
        if validate_file(file_path, strict=args.strict) != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
