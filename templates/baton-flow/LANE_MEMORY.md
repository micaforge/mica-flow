<!-- Versioned copy — source of truth: micaforge/baton-flow @ 04d91347ecca6bebef08c11ef5dd8c3131176369 (template/LANE_MEMORY.md). Folds update the source first and ripple here in the same act; do not edit this copy's substance here. -->

<!-- CENTRE-SECTION:BEGIN -->
<!-- CENTRE v1 is stamped here by the desk at lane birth. Lane: never write, edit, or restate this span. -->
<!-- CENTRE-SECTION:END -->
<!-- CENTRE-APPENDS:BEGIN -->
<!-- Lane notes + change requests for the centre, each with the workflow reason; the centre dispositions them on the sweep. -->
<!-- CENTRE-APPENDS:END -->
---
type: lane-memory
lane: <lane-slug>
crew: <crew / flow name>
chat_id: <side-chat id>
lead: <lead name + seat (chat <id>)>
updated: <YYYY-MM-DD>
status: active — <one-line state>
schema: 2
cap: 300
upkeep:
  - state + pointers only; the story lives in each cycle's JOURNAL, memory points into it, never holds it
  - JUST DID / NEXT updated at milestones
  - STICK section under NEXT, every entry dated with a named counterparty; undated doesn't count
  - prune in the act; cap measured minus the centre span
sot:
  - <charter path> (charter)
  - <boundary path> (boundary)
  - <package router path>
---

# LANE_MEMORY — <Lane name> (<crew>)

**Bench:** <what this lane holds, one line>
**Team:** <team declaration, one line>

**Inherits BY CHARTER from <predecessor bench>:** <instruments + method, named>
**Does NOT inherit:** <predecessor's queues, obligations, and history — stated, never left to silence>

**Owns (BOUNDARY):** <owned shapes / surfaces>
**Never:** <hard nevers, from BOUNDARY>

## JUST DID
- <YYYY-MM-DD> — <landed act, dated, with pointer to its record>

## NEXT
- <next act, with pointer to its source of truth>
- CENTRE v1 stamp: <pending — desk stamps the span at the top of this file; not written by this lane | landed <date>>
- On each cycle opened: that cycle carries a JOURNAL (seeded from baton-flow `template/JOURNAL.md`); this file points into it only.

### STICK
- Holding: <none | the stick, for <wave / cycle>> — <YYYY-MM-DD> · counterparty: <lead name + seat (chat <id>)>
- Passed: <none | to <counterparty>, for <wave / cycle>> — <YYYY-MM-DD> · counterparty: <name + seat (chat <id>)>
- Returned: <none | to the lead's gate, <wave / cycle>> — <YYYY-MM-DD> · counterparty: <lead name + seat (chat <id>)>

## Pointers
- <crew live state path>
- <cycle / record-of-record paths>
