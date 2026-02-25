# AICL: Agent Intent Communication Language

[![PyPI](https://img.shields.io/pypi/v/aicl)](https://pypi.org/project/aicl/)
[![License](https://img.shields.io/github/license/haocn-ops/aicl-protocol)](LICENSE)

AICL is a structured communication language for AI agents and human-agent collaboration.
It prioritizes low ambiguity, high efficiency, and auditable decision flow.

**🎮 Try it now**: [AICL Playground](https://haocn-ops.github.io/aicl-protocol/)

Status: `Final v1.0.0` (2026-02-25)

## Why AICL?

Modern AI agents need to communicate with each other—and with humans. But existing protocols are either:
- Too low-level (JSON, REST)
- Too verbose (XML)
- Not designed for agent autonomy

AICL fills this gap with **intent-first**, **constraint-aware**, and **negotiation-native** messaging.

## Quick Start

```bash
# 1. Install
pip install aicl

# 2. Parse an AICL message
aicl parse examples/01_ask.aicl --pretty

# 3. Validate messages
aicl validate --strict examples/

# 4. Transpile natural language to AICL
aicl transpile "please verify policy compliance for release"
```

**Or use the online playground**: https://haocn-ops.github.io/aicl-protocol/

## Core Goals

- Intent-first messaging
- Constraint-bound execution
- Evidence-aware reasoning
- Negotiation-native collaboration
- Human-in-the-loop (HITL) safety controls

## Message Model

```txt
MSG{
A:<Actors>
I:<Intent>
O:<Object>
T:<TaskGraph>
G:<Delegation>
C:<Constraints>
K:<Known>
U:<Unknown>
P:<Proposal>
R:<Risk>
Q:<Query>
D:<Decision>
V:<Votes>
M:<MemoryCapsule>
H:<HITL>
X:<Expectation>
S:<State>
}
```

## Required Fields

- Always required: `I`, `O`, `S`
- Multi-agent context: `A`
- Delegation: `T`, `G`
- Negotiation/decision flow: `D`
- High-risk operations: `R`, `H`

## Standard Intents (v1.0)

`ASK, INFORM, PLAN, ACT, VERIFY, NEGOTIATE, DELEGATE, ACCEPT, REJECT, ESCALATE, SUMMARIZE, COMPARE, ESTIMATE, PRIORITIZE, SCHEDULE, BLOCK, UNBLOCK, REPLAN, CANCEL, PAUSE, RESUME, COMMIT, ROLLBACK, AUDIT, TRACE, CITE, CLARIFY, CONFIRM, DISPUTE, RESOLVE, SPLIT, MERGE, ROUTE, HANDOFF, MONITOR, ALERT, REPORT, DIAGNOSE, FIX, TEST, VALIDATE, SANITIZE, FILTER, TRANSFORM, RETRIEVE, SYNTHESIZE, CRITIQUE, JUSTIFY, PREDICT, CLOSE`

## Conflict Resolution Priority

`policy > hitl > authority > evidence > feasibility > utility > vote`

## Minimal Validation Rules

- `S.conf` must be within `0.00..1.00`
- `S.ver` uses semantic versioning (e.g. `1.0`)
- `S.trace` must be globally unique
- No cyclic dependencies in `T.deps`
- `H.required=true` blocks high-risk `COMMIT` before human response

## Example

```txt
MSG{
A:{from=agent_planner,to=[agent_risk],role=planner}
I:NEGOTIATE
O:release/2026Q1
C:deadline=2026-02-26T12:00+08;policy=P1
K:[data_ready,legal_partial]
U:[final_legal_clause]
P:[ship_with_guard_clause]
R:[compliance_risk_if_unguarded]
H:{required=true,trigger=policy_risk,question="Allow guarded release?",options=[allow,delay,reject],sla=2026-02-25T21:30+08,default_action=delay}
X:need_human_choice_id
S:conf=0.61;ver=1.0;trace=trc_aicl_001
}
```

## Compare with Other Protocols

| Feature | AICL | OpenAI Agents SDK | MCP (Anthropic) | REST/JSON |
|---------|------|-------------------|-----------------|-----------|
| Intent-driven | ✅ | ❌ | ❌ | ❌ |
| Built-in Negotiation | ✅ | ❌ | ❌ | ❌ |
| HITL Safety Controls | ✅ | Partial | ❌ | ❌ |
| Constraint Propagation | ✅ | ❌ | ❌ | ❌ |
| Confidence Tracking | ✅ | ❌ | ❌ | ❌ |
| Human-Readable | ✅ | ✅ | ✅ | ❌ |
| Extensible | ✅ | ✅ | ✅ | ✅ |

AICL is designed specifically for **multi-agent collaboration** with built-in support for:
- Task delegation with capability matching
- Risk-aware decision making
- Human-in-the-loop approvals
- Auditable trace logs

## Roadmap

- Next: richer semantics and interoperability profiles

## Repository Structure

- `README.md`: quick overview
- `SPEC.md`: full v1.0 draft specification
- `ABNF.md`: textual grammar draft
- `examples/`: ready-to-use message samples
- `tools/validate_aicl.py`: validator (supports `--strict`)
- `tools/parse_aicl.py`: AICL text to JSON parser
- `tools/transpile_nl_to_aicl.py`: NL to AICL draft transpiler
- `tools/aicl_cli.py`: unified CLI (`parse`, `validate`, `transpile`)
- `tests/`: unittest suite
- `FINAL_VERSION.md`: release summary

## Validation

Run the validator against examples:

```bash
python3 tools/validate_aicl.py examples
python3 tools/validate_aicl.py --strict examples
```

Parse one AICL message into JSON:

```bash
python3 tools/parse_aicl.py --pretty examples/02_negotiate_hitl.aicl
```

Transpile a natural language request to AICL draft:

```bash
python3 tools/transpile_nl_to_aicl.py "please summarize weekly incidents"
```

Use unified CLI:

```bash
python3 tools/aicl_cli.py parse --pretty examples/02_negotiate_hitl.aicl
python3 tools/aicl_cli.py validate --strict examples
python3 tools/aicl_cli.py transpile "verify policy compliance for release"
```

Run tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
