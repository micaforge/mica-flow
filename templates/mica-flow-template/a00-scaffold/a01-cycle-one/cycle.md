---
type: cycle
status: outline
arc: "{{FLOW_NAME}}"
title: "{{CYCLE_ID}}: {{CYCLE_TITLE}}"
depends_on: [{{DEPENDS_ON}}]
---

# {{CYCLE_ID}}: {{CYCLE_TITLE}}

## Goal

{{CYCLE_GOAL}}

## Acceptance — gates

| # | gate | verify | pass |
|---|------|--------|------|
| G1 | {{GATE1}} | {{VERIFY1}} | {{PASS1}} |
| G2 | `_run/` contains brief's deliverables | ls `_run/` | all present |
| G3 | next cycle's BRIEF completed (if not last) | read next BRIEF.md | not an outline |
| G4 | verified against live data (not just thin/mocked) | {{LIVE_DATA_VERIFY}} | {{LIVE_DATA_PASS}} |

## Method

{{CYCLE_METHOD}}

## Findings

<!-- agent fills this during the cycle -->

## Decisions

<!-- proposals and rulings; nothing moves without lead sign-off -->
