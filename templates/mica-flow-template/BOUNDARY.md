# BOUNDARY.md — {{FLOW_NAME}} (flow)

<!-- Complete at seeding: name what this flow holds, where its
     data lives, and the lines it never crosses. Protocol:
     ~/workspace/reference/project-boundary.md. The table below is
     the standard shape (meta-forge exemplar). -->

## Intent

TODO: why this flow exists, its privacy posture (public /
internal / private), and what would make its output publishable.

## Data map

| Path | Class | Notes |
|------|-------|-------|
| `AGENT.md`, `ROUTER.md`, `RUNBOOK.md`, `TODO.md`, `LANE_MEMORY.md` | code | flow docs / lane state |
| `{{PREFIX}}NN-*/BRIEF.md`, `{{PREFIX}}NN-*/cycle.md` | code | cycle briefs + records |
| `{{PREFIX}}NN-*/_run/` | generated | run artifacts, evidence, reviews |
| TODO | TODO | external data this flow touches (path + class) |

Classes: `code` (authored) · `data` (inputs/records) ·
`generated` (outputs). Code, user data, and generated content
stay separated by structure — directories + gitignore — never by
memory.

## Hard lines

- TODO: secrets handling for this flow (default: no keys, tokens,
  or credential material in any file here — vault only; a secret
  value in a deliverable is a defect).
- TODO: anything this flow must never do / contact / publish.

## Worker contract

- heartbeat may: read-only
- on boundary violation: flag to the lead, never auto-fix by deleting
