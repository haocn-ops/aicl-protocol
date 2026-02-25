# AICL v1.0 Specification

## 1. Scope

AICL (Agent Intent Communication Language) is a structured language for:

- agent-to-agent communication
- human-agent coordination
- auditable and policy-aware decision exchange

## 2. Design Principles

- Intent-first: message starts with purpose, not narrative.
- Constraint-bound: cost/time/policy constraints are explicit.
- Evidence-aware: known facts and unknown gaps are separated.
- Negotiation-native: proposal/counter/accept/reject are first-class.
- Safety-governed: HITL escalation is standardized.

## 3. Canonical Message Shape

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

## 4. Field Requirements

- Required in all messages: `I`, `O`, `S`
- Required in multi-agent flow: `A`
- Required for delegation: `T`, `G`
- Required for explicit agreement state: `D`
- Required for high-risk operations: `R`, `H`

## 5. Intents

Standard v1.0 intents:

`ASK, INFORM, PLAN, ACT, VERIFY, NEGOTIATE, DELEGATE, ACCEPT, REJECT, ESCALATE, SUMMARIZE, COMPARE, ESTIMATE, PRIORITIZE, SCHEDULE, BLOCK, UNBLOCK, REPLAN, CANCEL, PAUSE, RESUME, COMMIT, ROLLBACK, AUDIT, TRACE, CITE, CLARIFY, CONFIRM, DISPUTE, RESOLVE, SPLIT, MERGE, ROUTE, HANDOFF, MONITOR, ALERT, REPORT, DIAGNOSE, FIX, TEST, VALIDATE, SANITIZE, FILTER, TRANSFORM, RETRIEVE, SYNTHESIZE, CRITIQUE, JUSTIFY, PREDICT, CLOSE`

## 6. Constraint and Safety Model

Typical `C` keys:

- `deadline`
- `cost<=...`
- `policy=<policy_id>`
- `len<=...`

HITL (`H`) is required when:

- policy or safety risk is present
- risk exceeds agreed threshold
- unresolved conflict exceeds SLA
- confidence is below threshold (for example `<0.55`)

## 7. Conflict Resolution Order

`policy > hitl > authority > evidence > feasibility > utility > vote`

## 8. Validation Rules

- `S.conf` must be `0.00..1.00`
- `S.ver` uses semantic versioning (`1.0`, `1.1`, ...)
- `S.trace` must be globally unique
- `T.deps` must be acyclic
- high-risk `COMMIT` is blocked if `H.required=true` and unresolved

## 9. Error Codes

- `E001_MISSING_REQUIRED_FIELD`
- `E002_INVALID_INTENT`
- `E003_INVALID_CONFIDENCE_RANGE`
- `E004_CONSTRAINT_CONFLICT`
- `E005_UNRESOLVED_TRACE`
- `E101_INVALID_NEGOTIATION_MODE`
- `E102_MISSING_DECISION_OWNER`
- `E103_CONFLICT_UNRESOLVED_TIMEOUT`
- `E104_ILLEGAL_OVERRIDE_POLICY`
- `E105_INSUFFICIENT_EVIDENCE_FOR_CLAIM`
- `E201_INVALID_TASK_GRAPH_REFERENCE`
- `E202_DELEGATION_CAPABILITY_MISMATCH`
- `E203_HANDOFF_FORMAT_VIOLATION`
- `E204_MEMORY_CAPSULE_INCOMPLETE`
- `E205_HITL_REQUIRED_BUT_SKIPPED`
- `E206_HITL_SLA_EXPIRED_NO_DEFAULT`

## 10. Interoperability Notes

- UTF-8 text is allowed; ASCII-first is recommended for portability.
- Field order should follow canonical shape for stable parsing.
- Unknown fields must be ignored unless policy disallows extensions.

## 11. Reference Tooling (v1.0.0)

- Parser: `tools/parse_aicl.py`
- Validator: `tools/validate_aicl.py`
- Strict validator mode: `--strict`
- NL draft transpiler: `tools/transpile_nl_to_aicl.py`
- Unified CLI: `tools/aicl_cli.py`
