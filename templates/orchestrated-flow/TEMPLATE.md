# Orchestrated flow — template

Scaffold a self-running flow with a persistent orchestrator.

## Scaffold

```bash
mica-flow <flow-name> "a01-scope,a02-…,a03-…,a04-synthesis" \
  --goal "<what the track produces>"
```

## a01 brief — write for the orchestrator

The a01 BRIEF.md names the orchestrator role explicitly. Template:

```markdown
## Task

You are the **persistent orchestrator** for this track. You own the
team, the schedule, and the synthesis. The lead (Mica) holds the map
and unblocks you; you run the day-to-day.

**Step 1 — Draft the shared brief** (`_run/shared-brief.md`).
[Questions / topics / scope.]

**Step 2 — Scope the team.** N roles, non-overlapping. Each gets a
one-page scope doc in `_run/roles/`.

**Step 3 — Sanity check with the lead.** Before dispatching, send a
terse summary. She confirms or redirects.

## _run/ conventions

- `_run/shared-brief.md` — the brief every specialist works from.
- `_run/roles/<role>.md` — one-page scope per specialist.
- `_run/findings/<topic>.md` — one file per question/topic.
- `_run/synthesis.md` — the final deliverable.

## Rules

1. Specialists are leaf agents (one level, no further spawning).
2. Bound each specialist: 30 min / 50 tool calls, read-only unless
   the brief says otherwise.
3. Every claim cites its source. Tag observed / inferred / unknown.
4. If your session ends mid-track, the continuation picks up from
   `_run/` — keep it current.
5. Durability: everything durable lives in `~/workspace` inside
   the project folder; the system layer is replaceable copies
   restored by a named floor; /tmp is scratch only.
```

## Dispatch the orchestrator

```
Spawn with the a01 brief. It drafts, scopes, sanity-checks, then
dispatches specialists per the sequenced plan.
```

## Continuity

If the orchestrator completes mid-track, spawn a continuation with:
- the prior `_run/` state,
- the lead's latest guidance,
- instructions to pick up at the current cycle.
