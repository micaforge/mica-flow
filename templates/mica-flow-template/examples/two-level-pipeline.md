# Example: Two-level pipeline flow

**When:** an outer iterative loop feeds jobs into per-job flows.
**Source:** mission-pipeline (2026-10-16) — Build Board mission processing.

## Structure

```
outer-flow/               # loops forever; a pipeline, not a project
  a01-scrape              # gather candidates
  a02-rank-gate           # decision tree → pick one
  a03-dispatch            # scaffold inner flow, loop back to a01

inner-flow-<job>/         # one per dispatched job
  a01-research → a02-scaffold → a03-build → a04-publish-gate
```

## Key rules

- The outer loop never "completes" — each pass dispatches or waits.
- The rank/gate cycle is the heart: every candidate passes through a
  decision tree (claimed? stale? tooling? budget?) before dispatch.
- Rejected candidates PARK with reasons, not deleted — re-evaluated each pass.
- Inner flows use the standard cycle pattern; each completes the next BRIEF.
- Human gates stay human (publish, final pick). Automation handles the rest.
