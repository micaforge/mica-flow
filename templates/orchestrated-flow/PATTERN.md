# Orchestrated flow pattern — self-running with a persistent orchestrator

A mica-flow variant where a dedicated orchestrator agent (not the lead)
owns day-to-day execution: scoping specialists, dispatching them, collecting
reports, and synthesizing. The lead holds the map and unblocks; the
orchestrator runs the work.

Case study: `muse-platform-research`, 2026-10-19. Four cycles
(scope → external-recon → internal-recon → synthesis), four specialist
roles, one orchestrator across the track.

## When to use it

- Multi-pronged work where specialists run in parallel (research, audits,
  recon, evaluations).
- The lead is overloaded (many lanes) and needs execution offloaded
  without losing the map.
- The work is bounded and read-only (research, surveys, reviews) — not
  open-ended builds.

## How it works

1. **Scaffold the flow** normally (`mica-flow <name> "a01-…,a02-…"`).
2. **Write the a01 brief for the orchestrator**, not a builder. The brief
   names the orchestrator role explicitly: owns the team, the schedule,
   the synthesis. The lead holds the map and unblocks.
3. **Spawn the orchestrator** with the a01 brief. It drafts the shared
   brief, scopes specialist roles, and sanity-checks with the lead before
   dispatching.
4. **Specialists are leaf agents** (one level — they don't spawn further).
   Each gets a bounded brief: task, exact sources/files, done criteria,
   stop conditions, budget (30 min / 50 calls).
5. **The orchestrator synthesizes** across cycles and completes each next
   cycle's BRIEF from findings. It reports to the lead at cycle boundaries.
6. **Continuity:** if the orchestrator's session ends mid-track, spawn a
   continuation with the prior `_run/` state + the lead's latest guidance.
   The `_run/` dir is the handoff, not the agent's memory.

## _run/ conventions

- `_run/shared-brief.md` — the brief every specialist works from.
- `_run/roles/<role>.md` — one-page scope per specialist (non-overlapping).
- `_run/findings/<topic>.md` — one file per question/topic.
- `_run/synthesis.md` — the final knowledge base or report.
- `_run/reflection-agent.md` / `_run/reflection-lead.md` — the
  closing reflection wave's two voices (final cycle).
- `_run/triage.md` — the reflection wave's scope-vs-framework
  triage + mirror verification.
- Every claim cites its source. Tag observed / inferred / unknown.

## What worked (muse-platform-research)

- **Orchestrator sanity-check gate.** It drafted the brief and checked with
  the lead before dispatching — caught scope issues early.
- **Bounded specialists.** 30 min / 50 calls each; they executed, didn't wander.
- **_run/ as handoff.** When the first orchestrator completed, the
  continuation picked up from `_run/` with zero context loss.
- **Lead stays captain.** The lead never managed specialists directly —
  just unblocked and sanity-checked at boundaries.

## The reflection wave — the mandatory final wave

A multi-wave flow closes with a reflection wave, not a summary.
The wave reviews THIS flow's own work — not other flows — and it
is the flow's self-improvement engine: a lesson that lives only
in a chat, a blocked lane, or a pending tap dies there.

1. **Two voices answer, in the record.** The agent (worker seat)
   and the lead each answer, independently: *what was missed?
   what drifted from the scope, the gates, or the original idea?
   what could have been done better?* Each voice lands as its own
   file in the final cycle's `_run/` — verbatim, not merged.
   Neither voice reads the other before writing.
2. **Triage every lesson — scope vs framework.** One table:
   `lesson | scope or framework | home(s) | mirror locations |
   status`. Scope → filed to the home flow and fixed there.
   Framework → not done until folded into the templates/examples
   **and** mirrored into every lane, skill, or standing file it
   applies to — in the same run, as part of the work.
3. **Mirrors are verified, not assumed.** The wave closes only
   when each framework item has been read back present in every
   location it belongs (grep/readback evidence in the triage
   record) — or is recorded as a user tap WITH its disposition.
   A recorded "no" is a decision, not a forgetting.
4. **Evolve + seed.** Revise the flow's own template/runbook
   with what the wave earned; write the next run's seed; name
   the next trigger (never blank).

Case study: template-steward arc 1, 2026-10-24. The two voices
independently converged on the arc's central miss, and the agent
voice caught a governance bend against the arc itself that no
earlier step had caught. Provenance: n=1 live run.

## Anti-patterns

- Don't use for open-ended builds — orchestrators coordinate, they don't
  architect.
- Don't let specialists spawn sub-agents — one level only.
- Don't skip the sanity-check — an unreviewed brief compounds errors
  across every specialist.
