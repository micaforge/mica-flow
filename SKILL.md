# mica-flow — multi-cycle agent orchestration

Use when a task is too big for one agent turn: research → build → review
work that needs briefs, gates, run records, and review cycles.

## What it is

mica-flow scaffolds and runs **rings**: named flows under
`~/workspace/flows/<name>/` where each cycle (`a01-…`, `a02-…`) is one
bounded agent run. A cycle has a `BRIEF.md` (the contract: task, files,
done criteria, budget), a `cycle.md` (goal + acceptance gates), and a
`_run/` directory (deliverables + evidence). Cycles run in order; each
agent completes the *next* cycle's BRIEF before finishing.

## Entry points

| Command | Does |
|---------|------|
| `mica flow run <name>` | scaffold a new flow (or resume one) |
| `mica flow status <name>` | per-cycle status, gates, `_run/` deliverables |
| `mica flow complete` | cross-flow completion report (all flows, % done) |
| `mica flow close <name> --verify` | verify all cycles done with evidence (gate before archiving) |
| `mica-flow` | legacy shim for the above |

## The cycle loop

1. **Lead** writes `aNN-<name>/BRIEF.md` (task, exact files in/out,
   done criteria, stop conditions, budget).
2. **Agent** executes the brief, writes deliverables to `_run/`,
   completes the *next* cycle's BRIEF.
3. **Lead** verifies gates in `cycle.md`, spot-checks 2–3 claims.
4. Repeat. Final cycle writes the flow summary; `mica flow close`
   verifies everything before archiving.

## Conventions

- `_run/` holds cycle reports and evidence — never ceremony.
- Agents execute the plan; they don't redesign it. Blocked or over
  budget → stop and report.
- Budget per cycle: 30 min / 60 tool calls.
- Keep flows lean; a cycle that only shuffles paper is a bug.

## Templates

Start from `templates/mica-flow-template/` — includes `AGENT.md`
(stage router), `RUNBOOK.md` (lead procedure), `TODO.md`, and the
`a00-scaffold` cycle skeleton. Copy, rename, fill in the BRIEF.
