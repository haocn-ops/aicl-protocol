#!/usr/bin/env python3
"""Unified CLI for AICL tools."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from parse_aicl import parse_file
from transpile_nl_to_aicl import transpile
from validate_aicl import validate_file


def cmd_parse(args: argparse.Namespace) -> int:
    data = parse_file(Path(args.path))
    if args.pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps(data, ensure_ascii=False))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    rc = 0
    paths: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            paths.extend(sorted(path.rglob("*.aicl")))
        else:
            paths.append(path)
    if not paths:
        print("No .aicl files found.")
        return 1
    for path in paths:
        if validate_file(path, strict=args.strict) != 0:
            rc = 1
    return rc


def cmd_transpile(args: argparse.Namespace) -> int:
    print(transpile(args.text, default_conf=args.conf))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AICL CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_parse = sub.add_parser("parse", help="Parse AICL into JSON")
    p_parse.add_argument("path")
    p_parse.add_argument("--pretty", action="store_true")
    p_parse.set_defaults(func=cmd_parse)

    p_validate = sub.add_parser("validate", help="Validate AICL files")
    p_validate.add_argument("paths", nargs="+")
    p_validate.add_argument("--strict", action="store_true")
    p_validate.set_defaults(func=cmd_validate)

    p_transpile = sub.add_parser("transpile", help="Transpile natural language to AICL draft")
    p_transpile.add_argument("text")
    p_transpile.add_argument("--conf", type=float, default=0.70)
    p_transpile.set_defaults(func=cmd_transpile)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

