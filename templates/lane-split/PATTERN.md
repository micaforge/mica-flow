# Lane-split pattern — reflection

Case study: the media power-tools, 2026-10-18. One SPEC.md → four lanes
(media-console, voicestudio-tie-in, postiz-tie-in, openmontage-eval), each
with its own flow, research assistant, and builders. Research + wave-1 done
in ~2.5h wall-clock.

## How it was done

1. **Spec first.** One `SPEC.md`: vision, then per lane — source, rework
   plan, tie-in, license posture. Grew 3 lanes → 4 when Curtis added
   OpenMontage. The spec is the parent; lanes are children.
2. **Recon.** Cloned each OSS repo and read actual code, not just READMEs.
   Briefs cited file:line, which is why builders didn't flail.
3. **Scaffold.** `mica-flow <lane> "a01-…,a02-…"` × 4. One wave = one
   builder, from the start.
4. **Pre-scope research assistants.** One side-chat worker per lane, briefed
   to fill the lane's a01 `BRIEF.md` from grounded research. No builder
   started from a vague brief.
5. **Parallel dispatch.** Four wave-1 builders at once, each with a bounded
   brief (task, files in/out, done criteria, stop conditions, budget).
6. **Relay + close.** Completions relayed to Curtis; the lead ran
   `mica flow close` per wave (never the builder).

## What worked

- **Research-before-build.** Every a01 brief was filled with verified
  citations before any builder spawned. Builders executed; they didn't
  discover.
- **Recon-first.** Grounding in real source prevented fantasy briefs —
  e.g. VoiceStudio's lazy engine registry (one-line seam), Postiz's public
  API shapes, OpenMontage's provider abstraction.
- **Crew-chain.** Researchers drafted the a02 brief as part of their
  deliverables, so the next wave was pre-briefed.
- **Bounded briefs with stop conditions.** Lane 3 (Postiz) stopped cleanly
  at an environmental blocker (docker pulls) instead of burning budget.
  A BLOCKED wave is a clean state, not a failure.
- **Parallel lanes.** Four lanes progressed concurrently; the lead's job
  was tracking, not building.

## Gaps — and the fixes

1. **Cross-lead dispatch collision.** Heartbeat and main dispatched the same
   4 a01 waves 10 minutes apart — 4 redundant builders. The `_run/` check
   alone can't prevent it (both saw empty dirs).
   → **Fix:** before dispatching, also `grep <flow-family>
   ~/workspace/.jarvis/agent-registry.jsonl | tail` for spawns in the last
   hour. If a duplicate is in flight, stand down. (In AGENTS.md.)
2. **Ephemeral recon.** A VM replacement wiped `/tmp` recon clones
   mid-research; two assistants re-cloned.
   → **Fix:** recon clones live under `~/workspace/recon/`, never /tmp.
   (In MEMORY.md.)
3. **Structural change mid-flight.** The flow flattening
   (`a00-scaffold/` removal) moved paths while three builders held the old
   ones; the lead redirected them via `subagent.send`.
   → **Fix:** briefs reference paths from the flow root; structural
   migrations check `subagent.list` / the agent registry for running
   builders first, and redirect rather than strand.
4. **Human-gate lanes need first-class marking.** Lane 3 blocked on Curtis's
   OAuth/Meta taps. It blocked cleanly — but the pattern should *declare*
   human gates up front: exact taps needed, who holds them, and that the
   lane parks (not fails) until they're done.
5. **No lane dashboard.** The lead relayed completions manually.
   → **Fix:** `LANES.md` at the parent — lane, flow, state, owner,
   blockers, human taps. One glance, whole project. (Template included.)
6. **The lead is the closer.** The media-console builder errored on a
   runtime issue at the very end; the lead verified the `_run/` evidence
   and ran the close gate. The pattern names this explicitly: builders
   never close their own waves.

## Toward the ideal

- **LANES.md as the parent view.** Not a status report — the working
  surface. The lead updates it per completion; Curtis reads it instead of
  asking "how'd it go."
- **Two dispatch modes, chosen per project** (see `diagram.svg`):
  parallel for independent lanes, sequential when lane N defines a schema
  lane N+1 builds on.
- **Research as a pre-cycle**, not an afterthought. The a01 brief is never
  written by the lead from memory — it's filled by a researcher from
  source.
- **A diagram per project**, generated in our taste — lanes, gates, human
  taps, feed-forward arrows. The picture is the plan.
- **The integration track starts late.** Lanes earn their keep first; the
  unification design begins only after 2+ lanes have closed wave-1. Don't
  unify prematurely.
