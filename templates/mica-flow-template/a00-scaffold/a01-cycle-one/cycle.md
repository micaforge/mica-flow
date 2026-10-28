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
| G5 | durability: deliverables + records inside the project folder under `~/workspace`; any system-layer copy named with its floor | file paths in `_run/` + summary | nothing durable outside the project tree |
| G6 | skills home: any reusable workflow/pattern/script/tool this cycle created is packaged under `~/skills/` | ls `~/skills/<package>/` | SKILL.md + skill.yaml present — or the cycle created nothing reusable |

## Method

{{CYCLE_METHOD}}

## Findings

<!-- agent fills this during the cycle -->

## Claims

<!-- present-tense claims this cycle's record makes; one row each.
     Rungs: 1 live behaviour · 2 artifacts on disk · 3 records only.
     A claim past its re-probe date is re-probed or downgraded,
     never silently carried. See RUNBOOK "Claims discipline". -->

| claim | rung | evidence | date | re-probe due |
|-------|------|----------|------|--------------|

## Decisions

<!-- proposals and rulings; nothing moves without lead sign-off -->
