---
type: cycle
status: outline
arc: "{{FLOW_NAME}}"
title: "{{CYCLE_ID}}: {{CYCLE_TITLE}}"
depends_on: [{{DEPENDS_ON}}]
---

# {{CYCLE_ID}}: {{CYCLE_TITLE}} (outline)

> Loose outline. The previous cycle's agent fills in goal, gates, and method.

## Goal

{{CYCLE_GOAL_OUTLINE}}

## Acceptance — gates

| # | gate | verify | pass |
|---|------|--------|------|
| G1 | {{GATE1}} | {{VERIFY1}} | {{PASS1}} |
| G2 | `_run/` contains brief's deliverables | ls `_run/` | all present |
| G3 | verified against live data (not thin/mocked) | {{LIVE_DATA_VERIFY}} | {{LIVE_DATA_PASS}} |

> **Dispatch check:** no cycle starts with G1 undefined. The agent
> completing the previous cycle fills in every gate cell — a bare
> TODO gate at dispatch is a defect, not a placeholder. (The close
> gate rejects bare TODO gates; the scaffold must not ship what
> the close forbids.)
