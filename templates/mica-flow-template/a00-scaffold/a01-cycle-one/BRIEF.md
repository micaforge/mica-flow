---
type: brief
status: ready
cycle: "{{CYCLE_ID}}"
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

## Deliverables → `{{CYCLE_ID}}/_run/`

1. `summary.md` — what was built, files touched, key findings.
{{NEXT_BRIEF_INSTRUCTION}}

## Done when

All gates in `cycle.md` pass.

---

*Acceptance lines in this brief are **bars set, not results
claimed** — they state what the cycle must clear, never what it
has achieved. Results live in the cycle's records, graded against
these bars at close.*
