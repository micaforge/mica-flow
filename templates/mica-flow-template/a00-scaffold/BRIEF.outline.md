---
type: brief
status: outline
cycle: "{{CYCLE_ID}}"
---

# BRIEF — {{CYCLE_ID}}: {{CYCLE_TITLE}} (outline)

> Loose outline. The agent completing the previous cycle fills this in fully
> based on actual findings. Report to your parent (the router), not the outline author.
>
> Brief-expansion standard: only the **first** brief of a new direction is
> written complete, by the lead. Later briefs start as outlines (this shape)
> and are expanded by the agent completing the previous cycle.

## Task (outline)

{{CYCLE_TASK_OUTLINE}}

## Builder kind

{{BUILDER_KIND_OUTLINE}}
<!-- e.g. "lite static builder" or "fullstack typescript builder".
     If the cycle needs artifact.edit, name the exact builder kind here.
     The router dispatches to the matching builder — a mismatch costs a cycle. -->

## Capability approvals

{{CAPABILITY_APPROVALS_OUTLINE}}
<!-- List any privileged capabilities (e.g. local.*.read) this cycle's work
     will need. These surface as approval cards to the human — never assume
     them granted. If denied, the agent stops and reports. -->

## Likely deliverables → `{{CYCLE_ID}}/_run/`

- `summary.md`
{{NEXT_BRIEF_OUTLINE}}

---

*Acceptance lines in this brief are **bars set, not results
claimed** — they state what the cycle must clear, never what it
has achieved. Results live in the cycle's records, graded against
these bars at close.*
