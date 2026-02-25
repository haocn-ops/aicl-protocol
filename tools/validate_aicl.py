#!/usr/bin/env python3
"""
Minimal AICL v1.0 validator.

Checks:
- required fields (I, O, S)
- intent membership
- S field contains conf/ver/trace
- conf range is 0..1
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


@dataclass
class ValidationError:
    code: str
    message: str


def parse_fields(text: str) -> dict[str, str]:
    match = re.search(r"MSG\s*\{(?P<body>.*)\}\s*$", text, flags=re.DOTALL)
    if not match:
        return {}
    body = match.group("body")
    fields: dict[str, str] = {}
    for line in body.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        fields[k.strip()] = v.strip()
    return fields


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


def validate_text(text: str) -> list[ValidationError]:
    errs: list[ValidationError] = []
    fields = parse_fields(text)
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

    return errs


def validate_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    errs = validate_text(text)
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
        if validate_file(file_path) != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())

