# Lane-split router — orchestration over time

The parent never builds. It tracks, sequences, and integrates. This is the
dispatch order for the life of a lane-split project.

## Wave 1 (all lanes)

Research assistants → filled a01 briefs → parallel builder dispatch →
relay → close gates → LANES.md updated.

Exception: a lane whose a01 depends on another lane's output runs
**sequential** — its builder dispatches after the upstream wave closes,
with the upstream's outputs appended to its brief.

## Wave 2+ (per lane, independent)

Each lane is its own flow with its own cycles. The researcher (or the
wave-1 builder, crew-chain pattern) drafts the next brief as part of the
wave-1 deliverables. The lead:

1. Reads the drafted next brief. Verifies it's concrete.
2. Collision-checks (PLAYBOOK step 3).
3. Dispatches the wave-2 builder for that lane only.

Lanes move at their own pace. A blocked lane parks; the others advance.
The lead never holds a healthy lane waiting for a blocked one.

## Adding a lane later

1. Add its section to the parent SPEC.md.
2. Recon → scaffold → research assistant → brief → dispatch.
   (PLAYBOOK steps 1–4, new lane only.)
3. Add its row to LANES.md.

Existing lanes are untouched. The diagram gets a new swimlane.

## The integration / unification track

Starts **only after 2+ lanes have closed wave-1**. It's a design flow
first, not a build flow:

1. Like/don't-like review across the lanes' outputs.
2. Design the unified surface: one library/store, one review/approve gate,
   one publish/distribution surface, shared provider abstractions.
3. Then — and only then — build waves against that design.

Don't unify prematurely. Lanes earn their keep first; the integration
design is informed by what actually shipped, not what was specced.

## Human gates

Some lanes block on Curtis (OAuth taps, credentials, account approvals,
budget). Mark them in the LANES.md "Human taps" column with the exact tap
**the moment the need is known** — the column is the live outstanding set.

The taps lifecycle (owned by this template):

- `mica lane taps` — unified view across all parents; `mica lane status
  --parent <dir>` — per-parent view. Both read LANES.md; the file is the
  source of truth.
- Present taps as tappable cards (`muse.create_options`): one question,
  2–4 options, each a complete reply. Batch them instead of dribbling one
  message at a time.
- When Curtis answers: clear the tap cell, log the decision + date in
  LANES.md's Log section. A resolved tap drops off `mica lane taps` on the
  next run — no separate bookkeeping.
- The lane parks with its unblock condition stated; a parked lane is a
  clean state.

## End of life per lane

A lane closes out when its cycles are done or its verdict is KILL
(evaluated and rejected — a clean, recorded outcome, like the avatar
spike). The parent SPEC notes the verdict; the flow stays as the record.
