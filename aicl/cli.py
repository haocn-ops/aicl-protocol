#!/usr/bin/env python3
"""AICL CLI - Command line interface for AICL."""

import argparse
import json
import sys
from pathlib import Path

from aicl.parser import parse_fields, parse_file
from aicl.validator import validate_message, validate_file


def cmd_parse(args):
    """Parse an AICL message file."""
    path = Path(args.path)
    data = parse_file(path)
    if args.pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps(data, ensure_ascii=False))


def cmd_validate(args):
    """Validate AICL message files."""
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


def cmd_transpile(args):
    """Transpile natural language to AICL (draft)."""
    # Simple rule-based transpiler
    text = args.text.lower()
    
    # Detect intent
    intent = "INFORM"
    if any(w in text for w in ["ask", "what", "who", "where", "when", "why", "how"]):
        intent = "ASK"
    elif any(w in text for w in ["verify", "check", "validate", "ensure"]):
        intent = "VERIFY"
    elif any(w in text for w in ["plan", "schedule", "organize"]):
        intent = "PLAN"
    elif any(w in text for w in ["do", "execute", "run", "deploy"]):
        intent = "ACT"
    elif any(w in text for w in ["delegate", "assign", "give"]):
        intent = "DELEGATE"
    elif any(w in text for w in ["negotiate", "discuss", "agree"]):
        intent = "NEGOTIATE"
    elif any(w in text for w in ["commit", "confirm", "approve"]):
        intent = "COMMIT"
    elif any(w in text for w in ["reject", "deny", "refuse"]):
        intent = "REJECT"
    
    # Build simple AICL message
    import time
    trace = f"trc_{int(time.time())}"
    
    aicl = f"""MSG{{
I:{intent}
O:{args.text}
S:conf=0.50;ver=1.0;trace={trace}
}}"""
    
    print(aicl)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AICL - Agent Intent Communication Language CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse AICL to JSON")
    parse_parser.add_argument("path", help="AICL file path")
    parse_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parse_parser.set_defaults(func=cmd_parse)
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate AICL files")
    validate_parser.add_argument("paths", nargs="+", help="AICL files or directories")
    validate_parser.add_argument("--strict", action="store_true", help="Enable strict checks")
    validate_parser.set_defaults(func=cmd_validate)
    
    # Transpile command
    transpile_parser = subparsers.add_parser("transpile", help="Transpile natural language to AICL")
    transpile_parser.add_argument("text", help="Natural language text")
    transpile_parser.set_defaults(func=cmd_transpile)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
