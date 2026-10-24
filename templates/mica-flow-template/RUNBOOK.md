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

## Claims discipline

A completion report is a claim, not a fact. Every claim a cycle
record states in the present tense — "live", "demonstrated",
"standing", "verified" — gets a row in the cycle's claims table
(`cycle.md`, `## Claims`):

| claim | rung | evidence | date | re-probe due |
|-------|------|----------|------|--------------|

- **Rungs, highest first:** 1 live behaviour (the thing answers
  now) · 2 built artifacts on disk · 3 records only. A claim cites
  the highest rung reached and a pointer (path:line, port, seq).
- **Present-tense claims expire.** At the re-probe due date the
  claim is re-probed or downgraded in the record — never silently
  carried forward. Live state decays (rollbacks, restarts, deploys)
  without any record being wrong when it was written.
- **Gate wording points at artifacts.** A gate that reads
  "demonstrated" or "verified" names the verification artifact in
  `_run/`, not the narrative around it.

The closer checks the claims table at the wave close gate: no
expired present-tense claims, no gate wording without its artifact.

*(Pattern source: implementation audit ia01–ia03, 2026-10-24 —
records are claims; verdicts climb the evidence ladder.)*

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
3. **Reworded gates state the claim in the headline.** If a gate
   closes with its claim reworded — narrowed, conditioned,
   qualified — the gate table's own pass cell carries the reworded
   claim (e.g. "PASS as reworded, with a live known gap: …"), never
   the original wording with the qualifier buried in Findings.
   A reader of the headline alone must get the true claim.
4. Closer records any decision checkpoints the wave produced
   (`_run/checkpoints.md`, OPEN until the user answers) and relays them.

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
