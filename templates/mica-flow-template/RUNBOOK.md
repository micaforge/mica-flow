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
