# AICL: Agent Intent Communication Language

AICL is a structured communication language for AI agents and human-agent collaboration.
It prioritizes low ambiguity, high efficiency, and auditable decision flow.

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

## Roadmap

- ABNF grammar hardening
- Reference validator
- Natural-language to AICL transpiler
- Multi-agent protocol test suite

