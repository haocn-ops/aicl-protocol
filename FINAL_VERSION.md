# AICL Final v1.0.0

Release date: 2026-02-25

## Included

- Core language docs: `README.md`, `SPEC.md`, `ABNF.md`
- Examples: `examples/*.aicl`
- Parser: `tools/parse_aicl.py`
- Validator: `tools/validate_aicl.py` with `--strict`
- NL transpiler: `tools/transpile_nl_to_aicl.py`
- Unified CLI: `tools/aicl_cli.py`
- Test suite: `tests/test_aicl_tools.py`

## Finalized CLI

```bash
python3 tools/aicl_cli.py parse --pretty examples/02_negotiate_hitl.aicl
python3 tools/aicl_cli.py validate examples
python3 tools/aicl_cli.py validate --strict examples
python3 tools/aicl_cli.py transpile "please summarize weekly incidents"
```

## Quality Gate

- Parser returns JSON for valid message blocks.
- Validator enforces required fields and intent whitelist.
- Strict validator enforces canonical field order and COMMIT safety checks.
- Unit tests pass via `python3 -m unittest discover -s tests -p 'test_*.py'`.

