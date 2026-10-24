---
type: ring
status: seeded
name: "{{FLOW_NAME}}"
created: "{{DATE}}"
---

# Ring: {{FLOW_NAME}}

{{FLOW_GOAL}}

## Cycles

{{CYCLE_LIST}}

## Gates (ring-level)

| # | gate | verify | pass |
|---|------|--------|------|
| G1 | every cycle's `cycle.md` status = done | grep status | all done |
| G2 | every `_run/` has its brief's deliverables | ls per cycle | none missing |
| G3 | no unresolved blockers | grep -r "blocked" _run/ | none found |

## State

<!-- the router updates this as cycles complete -->
- [ ] a01-{{CYCLE1}}:
- [ ] a02-{{CYCLE2}}:
- [ ] a03-{{CYCLE3}}:

## LANE_MEMORY

Every lane keeps one `LANE_MEMORY.md` — side chats in their chat
directory, chat-less lanes in the parent flow directory.

- **Hard cap 200 lines.** Current state + source-of-truth pointers
  + recall commands only — never history, never a copy of the
  records it points at.
- **Update on every completion and every decision**, pruning in
  the same edit: superseded decisions, resolved items, and stale
  lines come out (the pruned content lives in the records, not
  here).
- The parent registry (LANES.md) stays the registry and the lane
  index stays routing; LANE_MEMORY points at both, never copies
  them.

*(Pattern source: estate-wide lane practice, set 2026-10-21.)*
