#!/usr/bin/env python3
"""
AICL v1.0 parser (v0.1 implementation).

Converts AICL text messages into JSON.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def split_top_level(text: str, sep: str) -> list[str]:
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


def parse_scalar(text: str):
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


def parse_value(text: str):
    raw = text.strip()
    if raw.startswith("{") and raw.endswith("}"):
        return parse_object(raw[1:-1].strip())
    if raw.startswith("[") and raw.endswith("]"):
        return parse_list(raw[1:-1].strip())
    return parse_scalar(raw)


def parse_list(text: str) -> list:
    if not text:
        return []
    return [parse_value(item) for item in split_top_level(text, ",")]


def parse_object(text: str) -> dict:
    if not text:
        return {}
    obj: dict = {}
    for pair in split_top_level(text, ","):
        if "=" not in pair:
            # Preserve non key-value tokens as boolean flags.
            obj[pair] = True
            continue
        key, val = pair.split("=", 1)
        obj[key.strip()] = parse_value(val)
    return obj


def parse_fields(text: str) -> dict:
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
            # Allow compact state style: conf=0.8;ver=1.0;trace=t1
            data[key] = parse_object(raw_value.replace(";", ","))
        else:
            data[key] = parse_value(raw_value)
    return data


def parse_file(path: Path) -> dict:
    return parse_fields(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse AICL text into JSON.")
    parser.add_argument("path", help="AICL file path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    data = parse_file(Path(args.path))
    if args.pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps(data, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
