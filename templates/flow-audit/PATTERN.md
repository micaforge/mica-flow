# Flow Audit — optional final review wave

An independent reviewer audits a completed (or in-progress) mica-flow,
comparing planned vs delivered, validating scope changes, and reviewing
the next wave's brief before dispatch.

## When to use

- After a multi-cycle flow completes (or reaches a natural breakpoint)
- Before dispatching a new cycle that builds on prior work
- When scope has drifted (inserted cycles, renamed dirs, changed plans)

## What the auditor does

1. Read AGENT.md, ROUTER.md, each cycle's cycle.md + _run/summary.md
2. Per-cycle: planned vs delivered, gate status
3. Scope changes: what was added/changed, was it justified?
4. Next-wave brief review: is it dispatch-ready? Blockers? Overlaps?
5. Gaps: anything planned but not done? Done but not planned?

## Deliverable

`_run/flow-audit.md` — per-cycle verdicts, scope change analysis,
next-wave readiness, gaps, recommendations.

## Reference implementation

`~/workspace/flows/workspace-restructure/_run/flow-audit.md` (2026-10-19)
— audited a01-a07, caught a dispatch blocker (missing `data/`/`infra/` dirs).
