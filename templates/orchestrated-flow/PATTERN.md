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
- Every claim cites its source. Tag observed / inferred / unknown.

## What worked (muse-platform-research)

- **Orchestrator sanity-check gate.** It drafted the brief and checked with
  the lead before dispatching — caught scope issues early.
- **Bounded specialists.** 30 min / 50 calls each; they executed, didn't wander.
- **_run/ as handoff.** When the first orchestrator completed, the
  continuation picked up from `_run/` with zero context loss.
- **Lead stays captain.** The lead never managed specialists directly —
  just unblocked and sanity-checked at boundaries.

## Branch shape: the ripple

Mid-track, a wave's gate review can surface a branch-need: one
claim that must be tested, or one set of items that must be
graded, before the wave can honestly close. That branch is a
**ripple**:

- **Shape:** named trigger → brief → work → verdict. The ripple
  lives in the parent flow's records (`_run/ripples/<slug>.md`),
  inherits the parent's gates and vocabulary, and is bounded
  like any specialist task.
- **Gate discipline:** the gate review opens it — are the deltas
  real? is the evidence at the claimed rung? are the candidates
  triaged? The ripple resolves before the main arc passes the
  gate, or the gate passes **with the gap named and owned** in
  the gate record. Never silently.
- **Ripples don't ripple.** A ripple that needs a branch of its
  own escalates to the lead. One level keeps the shape honest.
- **Proven shapes:** the *review ripple* (grade all items for
  completion before proceeding) and the *probe ripple* (one
  load-bearing claim tested live before the wave proceeds — the
  brief for one lives in `templates/probe-brief/`).

Ripple findings feed the track's synthesis like everything else
the arc produces.

## Anti-patterns

- Don't use for open-ended builds — orchestrators coordinate, they don't
  architect.
- Don't let specialists spawn sub-agents — one level only.
- Don't skip the sanity-check — an unreviewed brief compounds errors
  across every specialist.
