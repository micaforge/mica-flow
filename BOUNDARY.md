# BOUNDARY.md — mica-flow

## Intent
public — the mica-flow multi-cycle flow scaffold (MIT).

## Data map
| Path | Class | Notes |
|------|-------|-------|
| `bin/`, `caps/`, `hooks/`, `tools/` | code | CLI + automation |
| `templates/` | code | flow templates (incl. lane-split) |
| `references/`, `workflows/` | code | docs + workflow definitions |
| `*.md` (README, SKILL, PACKAGE) | code | docs |
| `assets/` | code | icons/visuals |

## Git rules
- must-be-clean-before: push, publish
- never-commit: secrets, `*.db*`, `.env`
- audit: `mica-audit` before every push; no direct commits to
  `dev`/`master` — branch → PR, squash-merge; code PRs include/extend tests

## Worker contract
- heartbeat may: read-only
- on dirty status: report
- on boundary violation: flag to Derek, never auto-fix by deleting
