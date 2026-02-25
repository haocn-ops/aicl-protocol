#!/usr/bin/env python3
"""AICL validator module."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


INTENTS = {
    "ASK", "INFORM", "PLAN", "ACT", "VERIFY", "NEGOTIATE", "DELEGATE", 
    "ACCEPT", "REJECT", "ESCALATE", "SUMMARIZE", "COMPARE", "ESTIMATE", 
    "PRIORITIZE", "SCHEDULE", "BLOCK", "UNBLOCK", "REPLAN", "CANCEL", 
    "PAUSE", "RESUME", "COMMIT", "ROLLBACK", "AUDIT", "TRACE", "CITE", 
    "CLARIFY", "CONFIRM", "DISPUTE", "RESOLVE", "SPLIT", "MERGE", "ROUTE", 
    "HANDOFF", "MONITOR", "ALERT", "REPORT", "DIAGNOSE", "FIX", "TEST", 
    "VALIDATE", "SANITIZE", "FILTER", "TRANSFORM", "RETRIEVE", "SYNTHESIZE", 
    "CRITIQUE", "JUSTIFY", "PREDICT", "CLOSE"
}

KNOWN_FIELDS = ["A", "I", "O", "T", "G", "C", "K", "U", "P", "R", "Q", "D", "V", "M", "H", "X", "S"]
KNOWN_FIELD_SET = set(KNOWN_FIELDS)


@dataclass
class ValidationError:
    """Validation error."""
    code: str
    message: str


def parse_s_object(s_value: str) -> dict:
    """Parse the S field value."""
    raw = s_value.strip()
    if raw.startswith("{") and raw.endswith("}"):
        raw = raw[1:-1]
    raw = raw.replace(";", ",")
    data: dict = {}
    for part in raw.split(","):
        part = part.strip()
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        data[k.strip()] = v.strip()
    return data


def validate_message(text: str, strict: bool = False) -> list[ValidationError]:
    """Validate an AICL message.
    
    Args:
        text: The AICL message text
        strict: If True, enable strict validation checks
        
    Returns:
        List of validation errors (empty if valid)
    """
    errs: list[ValidationError] = []
    match = re.search(r"MSG\s*\{(?P<body>.*)\}\s*$", text, flags=re.DOTALL)
    if not match:
        return [ValidationError("E001", "Input is not a valid MSG{...} block.")]
    
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
    
    if not fields:
        return [ValidationError("E001", "No fields found in MSG block.")]
    
    # Required fields
    for required in ("I", "O", "S"):
        if required not in fields:
            errs.append(ValidationError("E001_MISSING_REQUIRED_FIELD", f"Missing required field: {required}"))
    
    # Intent validation
    intent = fields.get("I")
    if intent and intent not in INTENTS:
        errs.append(ValidationError("E002_INVALID_INTENT", f"Unknown intent: {intent}"))
    
    # S field validation
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
    
    # Strict mode validation
    if strict:
        unknown = [k for k in order if k not in KNOWN_FIELD_SET]
        if unknown:
            errs.append(ValidationError("E002_INVALID_INTENT", f"Unknown field(s): {', '.join(unknown)}"))
        
        ranks = [KNOWN_FIELDS.index(k) for k in order if k in KNOWN_FIELD_SET]
        if ranks != sorted(ranks):
            errs.append(ValidationError("E004_CONSTRAINT_CONFLICT", "Fields are not in canonical order."))
        
        if fields.get("I") == "COMMIT":
            if "R" not in fields:
                errs.append(ValidationError("E001_MISSING_REQUIRED_FIELD", "COMMIT in strict mode requires R field."))
            if "H" not in fields:
                errs.append(ValidationError("E205_HITL_REQUIRED_BUT_SKIPPED", "COMMIT in strict mode requires H field."))
    
    return errs


def validate_file(path: Path, strict: bool = False) -> int:
    """Validate an AICL file.
    
    Args:
        path: Path to the AICL file
        strict: If True, enable strict validation
        
    Returns:
        0 if valid, 1 if errors found
    """
    text = path.read_text(encoding="utf-8")
    errs = validate_message(text, strict=strict)
    if errs:
        print(f"[FAIL] {path}")
        for err in errs:
            print(f"  - {err.code}: {err.message}")
        return 1
    print(f"[OK]   {path}")
    return 0
