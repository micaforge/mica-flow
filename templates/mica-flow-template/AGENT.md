---
type: ring
status: seeded
name: "{{FLOW_NAME}}"
created: "{{DATE}}"
---

# Ring: {{FLOW_NAME}}

{{FLOW_GOAL}}

## The team

**You are a team of {{TEAM_CRAFT}} — not a single pair
of hands.** (Curtis's ruling, 2026-10-30: every flow's
AGENT.md opens with its team declaration — the craft in
one line, the seats and what each owns, and who leads.
A seat works its role to the whole team's standard.)

- **Lead:** {{LEAD_SEAT}} — holds the map for this
  flow, gates its cycles, decides at its tier.
- **Seats:** {{SEAT_ROLES}}
  <!-- one line per seat: name — what it owns. A
       single-seat flow still names its lead and the
       seats it pairs with (gate · reviewer · desk). -->
- Pairings and gate lines live in this file's cycles
  and the flow's ROUTER.md; the declaration names the
  team, the records name the work.

## Cycles

{{CYCLE_LIST}}

## Gates (ring-level)

| # | gate | verify | pass |
|---|------|--------|------|
| G1 | every cycle's `cycle.md` status = done | grep status | all done |
| G2 | every `_run/` has its brief's deliverables | ls per cycle | none missing |
| G3 | no unresolved blockers | grep -r "blocked" _run/ | none unresolved — a block carrying its deciding seat, the decision needed, and the date it was put to them is parked (a clean state), not unresolved |

These ring gates are the summary. The operative per-wave close is
the closer's C1–C5 check in RUNBOOK.md: C1 ↔ G1, C2 + C4 ↔ G2;
C3 (no bare TODO gates) and C5 (next cycle's BRIEF ready) are
close-only additions; G3 is checked at ring close.

## Status vocabulary

Ring `status:` (frontmatter above) — update it as the state
changes; a status left behind is a defect, not a default:

- `seeded` — scaffolded only; nothing dispatched yet.
- `active` — at least one cycle dispatched; not all closed.
- `done` — every cycle closed at its gates.

Cycle `status:` (cycle.md frontmatter):

- `outline` — goal and gates sketched; brief not yet complete.
- `ready` — brief complete; dispatchable.
- `done` — gates passed at the close gate.

## Durability — the three buckets

- **Durable:** files live in `~/workspace`, inside the
  project's own folder — the only guaranteed root.
- **System layer is replaceable copies** (units, /etc,
  /usr): source of truth stays in the project folder,
  copies are restored by a named floor, never
  hand-restored twice.
- **Scratch:** /tmp and home-outside-workspace are
  never durable — observed at best, wiped at worst.
  Anything needed later moves into the project folder
  before the session ends.
- **Named exception — skills:** `~/skills/` sits
  outside `~/workspace` by Curtis's adoption
  (2026-10-28, canary-verified durable). A flow that
  produces a reusable workflow, pattern, script, or
  tool names its `~/skills/` package as a close-out
  deliverable — scaffolded at the cycle that creates
  the thing, not retrofitted later.

## Decision points — class at source

A decision point in this flow is classed before it
surfaces anywhere, under the tap-triage rubric
(`templates/tap-triage/PATTERN.md` in the mica-flow
template set): six ordered tests, first match wins →
Curtis; no match → decidable at desk/Mica, logged
here with overrule standing. A point missing its
premises bounces back for a complete packet — it
never routes upward half-formed.

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

## Cycle naming convention (2026-10-19)

Cycles use project-specific prefixes, not generic `aNN`:

- Each flow defines a 1-2 letter prefix in ROUTER.md (e.g. `workspace-docs` → `d`, `workspace-restructure` → `r`, `decision-taps` → `t`)
- Cycles: `<prefix><NN>` (e.g. `d01`, `d02`, `r01`)
- Sub-phases: `<prefix><NN>.<MM>` (e.g. `r03.01`, `r03.02`) — dot notation, not letter suffixes like `r03b`

Existing flows with `aNN` names keep them (no retroactive rename).
