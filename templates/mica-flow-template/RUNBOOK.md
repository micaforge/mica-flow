# RUNBOOK — running a mica-flow

Distilled from soma-rings' lead procedure, trimmed for small rings.

## Cast

1. Read the cycle's `BRIEF.md` fully before spawning.
2. Check the brief's **Builder kind** — dispatch to the matching builder.
   A lite builder on a typescript task (or vice versa) wastes a full cycle.
3. Spawn one agent per cycle, in order. Never overlap cycles.
4. The brief is the contract: what to read, what to write, rules, budget.

## Capability approvals

- If the brief lists privileged capabilities, expect approval cards to the human.
- Never assume granted. If the human denies, the agent stops and reports —
  do not work around it.

## Harvest

1. When the agent reports done, read its `_run/` deliverables.
2. Spot-check 2–3 claims against cited files/lines.
3. If deliverables are missing or wrong, send the agent back — do not advance.

## Close the wave (the closer role)

Every wave names 1–2 **closers** — not the builder. The closer's only job
is the scaffold + runbook close steps; the builder never closes its own
wave. This is what keeps a multi-wave flow from drifting into "the lead
just implements it" by wave three.

1. Closer runs the per-wave gate: `mica flow close <flow> --cycle <name>`
   (C1 cycle done · C2 `_run/` holds deliverables · C3 no bare TODO gates ·
   C4 brief deliverables all present · C5 next cycle's BRIEF exists, ready,
   no TODOs). Exit 1 = BLOCKED: fix or escalate, do not advance.
2. **Never dispatch wave N+1 until wave N passes the close gate.**
   A failed close is a stop, not a suggestion.
3. Closer records any decision checkpoints the wave produced
   (`_run/checkpoints.md`, OPEN until the user answers) and relays them.

**The flow's final wave is a reflection wave.** When the last wave
closes, the closer also runs it — two voices, triage, verified
mirrors. Method: `templates/orchestrated-flow/PATTERN.md`,
"The reflection wave".

## Harvesting patterns into the templates

When a flow proves a pattern the templates don't carry (or carry
wrong), the fix lands as a PR into this repo — one PR per pattern,
branch `steward/<slug>`, provenance line naming the proving
flow(s). The gate reviews; pattern-level changes (new template,
retired template, changed gate semantics) go to the user as a tap.

The harvest runs under six rules (template-steward arc 1,
2026-10-24 — each one a lesson that arc paid for):

1. **Committed-identity preflight.** Before grading or editing,
   record `git status` + HEAD of the template repo in the
   deliverable. Grade and edit against `origin/main`; anything
   that exists only in a working tree is UNCOMMITTED and marked
   as such — never graded or cited as set content.
2. **Placement.** A new file inside an existing template family
   is the seat's call. A new family is flagged to the gate
   *before* the PR opens — never landed as a default.
3. **Disposition check.** Before the harvest brief is written,
   every inventory note (stale, contradictory, missing) maps to
   a grading row, a PR, or an explicit "noted, not harvested"
   line. Unmapped notes drop silently; mapped ones can't.
4. **Proof counts travel.** A candidate's proof count rides with
   it: inventory → brief ("Proven: <flow>, n=<count>") → the PR's
   provenance line repeats it. The gate sees n=1 without
   cross-reading the survey.
5. **Parallel seats, one record shape.** Multi-PR harvests split
   across seats; every seat appends to one shared table with
   fixed columns: `branch | PR | files | scope | provenance`.
   The merged record is a concatenation, not a re-derivation.
6. **Worktree end-state, named in the brief.** One worktree per
   PR branch, off `origin/main` — never edit the repo's primary
   working tree. The brief states when and by whom worktrees are
   removed (e.g. "leave in place until the gate's merge report,
   then the seat removes them"). No orphan worktrees by default.

## Decision checkpoints

When a wave hits a fork only the user can resolve (two defensible
designs, a wording choice, a scope question): write it as a **decision
checkpoint** — one question, 2–4 options each with a one-line trade-off,
visual reference where the choice is visual — in the cycle's
`_run/checkpoints.md` as **OPEN**. Relay it to the user as a tappable
card (`muse.create_options`): index card first when several are open,
then one card per checkpoint, each option a complete reply. The user
taps; record the decision with date, then resolve any brief items marked
"pending CPN" to the decision. Never invent the user's answer; an
unanswered checkpoint stays open, not defaulted. Full procedure:
`workflows/01-decision-checkpoints.md`.

## Gates

1. Check the cycle's gates table in `cycle.md` — every gate must pass.
2. Verify the next cycle's BRIEF is completed (not just outlined).
3. Update the ring's `## State` checklist.

## Rotate

If you (the lead) are rotating mid-run:
- [ ] Every running agent named with id, task, deliverable path
- [ ] Every next cycle has a READY brief (no "successor will write it")
- [ ] Ring `## State` is current
- [ ] Every repo touched: committed + pushed

## Rules

- Budget per cycle: 30 min / 60 tool calls. Stop and report if exceeded.
- If blocked, report the blocker. Do not improvise a new plan.
- A finished agent with warm context: repurpose for the adjacent task before killing.
