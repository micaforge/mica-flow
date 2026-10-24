# Probe brief — one load-bearing claim, tested by an independent seat

**Use when:** a gate, a record, or a plan rests on one claim that
can be tested directly — *the standing deployment refuses X*, *the
round-trip still works*, *the fix is live* — and the cost of the
claim being wrong is higher than the cost of testing it. The probe
is a bounded side-branch (a ripple) commissioned *before* the wave
proceeds on the claim: named trigger → this brief → the probe →
a verdict the gate can use.

**Not a review.** A review reads records. A probe touches the live
thing, under controls, and reports raw evidence. If the claim
can't be tested against the live system, it isn't a probe — it's
an audit item.

## The seat

- **Independent.** The probe seat is never the seat that built the
  thing or wrote the record under test — finder ≠ checker. It
  holds no stake in either answer.
- **One question.** The brief names exactly one load-bearing
  question. Anything else the seat notices is a footnote, not a
  second probe.
- **Bounded.** Named target, named method, test material only,
  budget stated up front. No fixes: the probe reports; it never
  repairs what it tests.

## The brief (fill in)

```markdown
# Probe: <the single load-bearing question, as a yes/no>

Seat: <who commissions> · Target: <the live system/record>
Method: <the original test being re-run, or the new test>
Bounds: <test material only / read-only / what must not be touched>

## Method

1. Establish the target's identity BEFORE the test (see record §1).
2. Controls first: <the negative controls — the inputs that must
   be refused> + a state check after them.
3. The test itself: <exact steps>.
4. Sanity control: <the legitimate path completing normally —
   proves the target discriminates rather than merely refusing
   (or accepting) everything>.
5. Cleanup: <return the target to its found state; name what
   "found" means>.
```

## The record

The probe files one record, in this order:

1. **Identity before the test.** What exactly was probed: unit /
   version / build hash + provenance, config and policy in force,
   state at open (locked/unlocked, counts, chain head) — plus
   anything that bounds the conclusion (e.g. a restore cadence
   that makes the identity stable across boots, or one that
   makes it a single instance's). A verdict about "the system"
   that was measured on an unidentified instance is void.
2. **Controls first.** The refusals, run before the attempt, each
   with the raw response and its audit/log sequence — and the
   state check proving the controls changed nothing.
3. **The test, as raw evidence.** Exact requests, exact responses,
   sequence numbers. Paraphrase is not evidence.
4. **The sanity control.** The legitimate path, exercised after
   (or before) the test, completing normally.
5. **Probe-side errors, recorded.** The seat's own mistakes —
   wrong id, wrong parser, wrong path — go in the record with
   their consequences, not edited out. A probe that hides its
   errors teaches the next seat to repeat them.
6. **Cleanup / final state.** What the probe left behind: test
   artefacts in terminal states, target untouched or restored,
   verification checks re-run and passing.
7. **One-line verdict.** The answer to the brief's question, and
   nothing else decided. The record names what is *not* the
   seat's call (the wording fix, the gate ruling, the follow-up)
   and leaves it to the seat that owns it. Evidence above the
   line; the decision it feeds belongs to someone else.

## Rules

- Test material only, unless the brief explicitly authorises
  otherwise — and then the bounds say exactly how far.
- If the target's identity can't be established, stop and report
  that. An unidentified target is the finding.
- If reality contradicts the brief's premise (the thing isn't
  deployed, holds real data, differs from its records), stop and
  report the contradiction. Don't improvise a new probe.

## Origin

Abstracted from a live probe run 2026-10-24 in the
implementation-audit flow (ia02): an adversary retest's bypass
claim re-run against the standing deployment of a credential
broker — deployment identity tabled first (byte-identical build,
restore cadence noted), negative controls denied and audited,
the claimed bypass reproduced with raw responses + audit
sequence numbers, a legitimate-path decide as the sanity
control, the seat's own invocation error recorded, cleanup
verified, verdict in one line. The record was sufficient for
the gate to rule on without a second reading.
