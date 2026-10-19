# lane-split — template for multi-faceted projects

**Use when:** a project has 2+ independent-but-related workstreams that each
deserve their own flow, their own research, and their own builder — but roll
up to one vision. The media power-tools (4 lanes: media-console,
voicestudio-tie-in, postiz-tie-in, openmontage-eval) are the worked example.

**The shape:**
```
Parent SPEC (vision + lane list)
  └── Lane 1 → its own flow → research → build waves → close gates
  └── Lane 2 → its own flow → research → build waves → close gates
  └── ...
  └── Integration / unification track (later, once lanes earn their keep)
```

**The lead never builds.** The lead writes the spec, scaffolds the lane
flows, briefs research assistants, dispatches builders, runs close gates,
and tracks the LANES.md registry. Building is the builders' job.

**Two dispatch modes** (see `diagram.svg`):
- **(a) Parallel** — lanes are independent; all research, then all wave-1
  builders, at once. Default.
- **(b) Sequential** — lane N's output feeds lane N+1's research. Use when
  lanes share a schema, API, or library the earlier lane defines.

**Files in this template:**
- `PATTERN.md` — the reflection: case study, what worked, gaps, improvements
- `PLAYBOOK.md` — the exact tool-call sequence, step by step
- `ROUTER.md` — orchestration: next waves per lane, adding lanes, the
  integration track
- `LANES.md` — the parent-level lane registry (copy per project)
- `diagram.svg` — the visual: parallel vs sequential, in our taste
