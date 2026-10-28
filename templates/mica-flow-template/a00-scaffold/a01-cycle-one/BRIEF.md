---
type: brief
status: ready
cycle: "{{CYCLE_ID}}"
class: design
---

# BRIEF — {{CYCLE_ID}}: {{CYCLE_TITLE}}

## Read first

- `../AGENT.md` (stage router)
- `../../RUNBOOK.md` (lead procedure — the rules that bind you)
- `cycle.md` (this cycle's goal and gates)

## Task

{{CYCLE_TASK}}

## Builder kind

{{BUILDER_KIND}}
<!-- If this cycle uses artifact.edit, name the exact builder kind required
     (e.g. "fullstack typescript builder"). A mismatch costs a full cycle. -->

## Capability approvals

{{CAPABILITY_APPROVALS}}
<!-- List privileged capabilities this work needs (e.g. local.*.read).
     These surface as approval cards to the human. Never assume granted —
     if denied, stop and report. -->

## Rules

1. Read-only outside the files this brief names.
2. Cite every claim (file:line). Tag observed / inferred / unknown.
3. Budget: 30 min / 60 tool calls. Stop and report if exceeded.
4. Durability: everything this cycle produces lives in
   the project folder under `~/workspace`. System-layer
   files are replaceable copies restored by a named
   floor — never the only copy. /tmp is scratch only.

## Claims register

<!-- Every load-bearing factual claim this cycle's work
     states or depends on — each with the source it rests
     on, the date that source was ruled, and the claim's
     owner. REQUIRED and filled for production briefs
     (frontmatter `class: production`): the flow lint
     refuses a production brief without one — no
     register, no production. Other classes may leave
     the table empty. A claim whose source is a dated
     preview or an unruled framing reads as stale at a
     glance; that visibility is the point. (Born from
     the ef03 teaser premise failure, 2026-10-28.) -->

| Claim | Source | Date ruled | Owner |
|-------|--------|------------|-------|

## Deliverables → `{{CYCLE_ID}}/_run/`

1. `summary.md` — what was built, files touched, key findings.
2. If this cycle creates a reusable workflow, pattern,
   script, or tool: its `~/skills/` package (SKILL.md +
   skill.yaml), scaffolded in THIS cycle — a close-out
   deliverable, not a retrofit.
{{NEXT_BRIEF_INSTRUCTION}}

## Done when

All gates in `cycle.md` pass.

---

*Acceptance lines in this brief are **bars set, not results
claimed** — they state what the cycle must clear, never what it
has achieved. Results live in the cycle's records, graded against
these bars at close.*
