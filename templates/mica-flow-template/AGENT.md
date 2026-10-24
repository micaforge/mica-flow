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

## Arc triggers + anti-stall

A ring that waits to be told to start will stall. Name this
ring's triggers in its charter — the events that open the next
arc without anyone dispatching it (an estate-wide audit closes ·
a lane closes with a new proven pattern · N days pass since the
last arc closed — pick the ones that fit, but pick some). Then:

- **The next trigger is always named.** The ring's LANE_MEMORY
  (or this State section) carries a "next arc trigger" line —
  never blank, never "TBD". The closing cycle re-names it.
- **A block is a routing address.** Every blocked item names the
  deciding seat, the exact decision, and the date it was put to
  them. "Pending" without those three is a stall, not a state.
- **Untapped gates don't wait forever.** A gate outside the
  user's no-expiry tier (personal affairs, money, public
  publishing, credentials, irreversible acts) that sits untapped
  past the standing window is the lead's to decide by the user's
  recorded patterns — logged, reported, overrule stays the
  user's.
