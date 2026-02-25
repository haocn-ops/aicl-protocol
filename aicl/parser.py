#!/usr/bin/env python3
"""AICL parser module."""

import re
from pathlib import Path
from typing import Any


def split_top_level(text: str, sep: str) -> list[str]:
    """Split text by separator, respecting nested braces/brackets and quotes."""
    parts: list[str] = []
    depth_brace = 0
    depth_bracket = 0
    in_quote = False
    quote_char = ""
    start = 0

    for i, ch in enumerate(text):
        if in_quote:
            if ch == quote_char:
                in_quote = False
            continue
        if ch in ("'", '"'):
            in_quote = True
            quote_char = ch
            continue
        if ch == "{":
            depth_brace += 1
            continue
        if ch == "}":
            depth_brace -= 1
            continue
        if ch == "[":
            depth_bracket += 1
            continue
        if ch == "]":
            depth_bracket -= 1
            continue
        if ch == sep and depth_brace == 0 and depth_bracket == 0:
            parts.append(text[start:i].strip())
            start = i + 1

    parts.append(text[start:].strip())
    return [p for p in parts if p]


def parse_scalar(text: str) -> Any:
    """Parse a scalar value."""
    raw = text.strip()
    if len(raw) >= 2 and ((raw[0] == '"' and raw[-1] == '"') or (raw[0] == "'" and raw[-1] == "'")):
        return raw[1:-1]
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    return raw


def parse_value(text: str) -> Any:
    """Parse a value (scalar, list, or object)."""
    raw = text.strip()
    if raw.startswith("{") and raw.endswith("}"):
        return parse_object(raw[1:-1].strip())
    if raw.startswith("[") and raw.endswith("]"):
        return parse_list(raw[1:-1].strip())
    return parse_scalar(raw)


def parse_list(text: str) -> list:
    """Parse a list value."""
    if not text:
        return []
    return [parse_value(item) for item in split_top_level(text, ",")]


def parse_object(text: str) -> dict:
    """Parse an object value."""
    if not text:
        return {}
    obj: dict = {}
    for pair in split_top_level(text, ","):
        if "=" not in pair:
            obj[pair] = True
            continue
        key, val = pair.split("=", 1)
        obj[key.strip()] = parse_value(val)
    return obj


def parse_fields(text: str) -> dict:
    """Parse AICL message text into a dictionary."""
    match = re.search(r"MSG\s*\{(?P<body>.*)\}\s*$", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Input is not a valid MSG{...} block.")
    body = match.group("body")
    data: dict = {}
    for line in body.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        raw_value = value.strip()
        if key == "S" and not (raw_value.startswith("{") and raw_value.endswith("}")) and "=" in raw_value:
            data[key] = parse_object(raw_value.replace(";", ","))
        else:
            data[key] = parse_value(raw_value)
    return data


def parse_file(path: Path) -> dict:
    """Parse an AICL file."""
    return parse_fields(path.read_text(encoding="utf-8"))
