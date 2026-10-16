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
| G1 | TODO | TODO | TODO |
| G2 | `_run/` contains brief's deliverables | ls `_run/` | all present |
| G3 | verified against live data (not thin/mocked) | TODO | TODO |
