# Reference — The escalation packet

**Use when:** a block has to travel up — worker → lead → gate →
the user's tap tier. A block that travels as a vibe ("it's
stuck") dies at every hop. A block that travels as a packet
arrives decidable.

## The packet (five parts, in order)

1. **Claim.** The blocked item in one sentence, stated so it can
   be checked and found true or false.
2. **Pointer.** The file:line (or record) where the block lives —
   the receiver opens the evidence, not a summary of it.
3. **Verified vs unknown.** What the sender has checked firsthand,
   and what is still unknown — labelled separately, never blended
   into one confidence.
4. **Recommendation.** What the sender would do, and the one-line
   why. A packet without a recommendation asks the receiver to do
   the sender's work.
5. **Tier call.** Whose decision this is — lead, gate, or the
   user's tap tier — and which waiting rule applies: the
   no-expiry class (personal affairs, money, public publishing,
   credentials, irreversible acts — waits for the user
   indefinitely) or the standing untapped window (the lead
   decides by recorded patterns, logged and reported).

## Example

> **Claim:** the build cannot start — every database slot in the
> free tier is taken (3 of 3 projects exist).
> **Pointer:** the lane's step-2 record (console readback, dated).
> **Verified:** the readback lists 3/3 projects and 0 secrets;
> the target project's scope is empty.
> **Unknown:** whether the user prefers paying for a fourth slot
> over reusing the empty one.
> **Recommendation:** reuse the empty project with a dedicated
> scoped account; delete it wholesale after the event.
> **Tier:** the gate decides the reuse; the paid upgrade is the
> user's (money — no-expiry).

## Provenance

**Practice-proven, form-new.** The estate's gates ran on this
packet shape through the 2026-10-24 implementation audit —
claims arrived with pointers, verified-vs-unknown stayed
labelled, judgment calls carried recommendations and a tier —
but the shape existed only as practice, never as written
boilerplate, until template-steward arc 1 (ts02) wrote it here.
