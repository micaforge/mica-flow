# Example: Dual-agent scope/research

**When:** a cycle needs both deep design and reality-checking.
**Source:** cap-packages a02 (2026-10-16).

## Structure

One cycle, two agents dispatched in parallel:

- **Agent A (architect):** designs from the contract/spec. Handles edge cases,
  writes drafts, writes tests. Works top-down.
- **Agent B (researcher):** hands-on validation. Runs the real tools, builds
  throwaway test cases, hunts for counter-evidence. Works bottom-up.
  Explicitly instructed to refute the design where it's wrong.

## Key rules

- B's brief must say "be brutal about refuting" — otherwise both agents
  confirm each other and you learn nothing.
- A designs, B breaks. The router synthesizes.
- Both read the same contract/spec first so they're testing the same thing.
