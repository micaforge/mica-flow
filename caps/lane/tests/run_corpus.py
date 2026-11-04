#!/usr/bin/env python3
"""Stage 3's regression corpus: the C7 calibration's cases, rebuilt
as mechanism-faithful fixtures (the calibration run of 2026-11-04,
a06 _run/calibration-c7-2026-11-04.md). Every rejection instance the
calibration itemizes by cause is here (15), plus its 1 verified
pair, plus 5 positive controls proving the resolver still pairs
when it should. The shipped resolver is graded against the run that
bound it: rejections must NOT pair; the pair and the controls MUST.

Provenance per case is noted inline; two strings are verbatim from
the live tree (the m03 cycle's `status: done` · mk03's status
string, still live at build time). The verified pair's original
queue line no longer exists in the wild — the lane corrected it in
the act on 2026-11-04, citing the calibration — so its line is
rebuilt to the calibration's recorded shape.

Run: python3 run_corpus.py [--compiler PATH]
Exit 0 iff every case grades as expected.
"""
import importlib.util
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_compiler(path):
    spec = importlib.util.spec_from_file_location("board_compiler",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def case(name, flows, line, files, expect_pair, cause):
    return {"name": name, "flows": flows, "line": line,
            "files": files, "expect_pair": expect_pair, "cause": cause}


def cyc(status, extra=""):
    return f"# cycle\nstatus: {status}\n{extra}"


CASES = [
    # --- the verified pair (calibration: 1) ---
    case("pair-memory-bank-m03", ["memory-bank"],
         "m03-implement wave 3 WAITING on Curtis's review tap, "
         "waves 1+2 done",
         {"workspace/flows/memory-bank/m03-implement/cycle.md":
          cyc("done")},          # status string verbatim, live tree
         True, "the calibration's verified pair"),

    # --- cross-flow collisions, unscoped (calibration cause: 5) ---
    case("rej-xflow-steward-w02", ["template-steward"],
         "w02 template sweep: fold the standing text → steward",
         {"workspace/flows/whole-idea/w02-driver/cycle.md":
          cyc("done")},
         False, "R1: w02 is whole-idea's, not the citing flow's"),
    case("rej-xflow-studio-w02", ["whole-idea-studio"],
         "w02 gallery pass: still building → studio",
         {"workspace/flows/whole-idea/w02-driver/cycle.md":
          cyc("done")},
         False, "R1: cross-flow id collision"),
    case("rej-xflow-studio-w03", ["whole-idea-studio"],
         "w03 walkthrough: in flight → studio",
         {"workspace/flows/whole-idea/w03-stage/cycle.md":
          cyc("done")},
         False, "R1: cross-flow id collision"),
    case("rej-xflow-generic-a", ["lane-x"],
         "q07 audit: open and running → x",
         {"workspace/flows/lane-y/q07-audit/cycle.md": cyc("done")},
         False, "R1: cross-flow id collision"),
    case("rej-xflow-generic-b", ["lane-p"],
         "r12 review: awaiting the seat → p",
         {"workspace/flows/lane-q/r12-review/cycle.md": cyc("done")},
         False, "R1: cross-flow id collision"),

    # --- mention-scoped sibling flows (calibration cause: 2) ---
    case("rej-mention-prism-a", ["prism-routing"],
         "pv02 route check, per flows/prism-vision/ notes → lead",
         {"workspace/flows/prism-vision/pv02-routes/cycle.md":
          cyc("done")},
         False, "R1: a mentioned flow never widens scope"),
    case("rej-mention-prism-b", ["prism-routing"],
         "pv03 route check, per flows/prism-vision/ notes → lead",
         {"workspace/flows/prism-vision/pv03-routes/cycle.md":
          cyc("done")},
         False, "R1: a mentioned flow never widens scope"),

    # --- the cited file's head naming a DIFFERENT cycle (cause: 1) ---
    case("rej-r4-sm03", ["stage-manager"],
         "sm03 relay prep — blocked-on: "
         "~/workspace/flows/stage-manager/sm03-cycle/cycle.md",
         {"workspace/flows/stage-manager/sm03-cycle/cycle.md":
          "# sm03 relay\n## note: sm01 CLOSED at its gate "
          "(2026-10-20)\nstatus: in flight\n"},
         False, "R4: evidence anchors to the cited record's own "
                "state, not a close word about another cycle"),

    # --- sub-cycle resolved to its parent (cause: 1) ---
    case("rej-r6-a04-1", ["workspace-docs"],
         "a04.1 annex pass: still open → lead",
         {"workspace/flows/workspace-docs/a04-annex/cycle.md":
          cyc("done")},
         False, "R6: a04.1 is a distinct citation; no parent "
                "fallback"),

    # --- cross-DESK packet number (cause: 1) ---
    case("rej-r3-packet-0003", ["main-seat"],
         "packet 0003: the desk item still rides → mica",
         {"skills/dev-desk/completed/0003-muse-call-display/"
          "REQUEST.md": "# a different desk's 0003\n"},
         False, "R3: a bare number never cross-desk matches"),

    # --- status-word overmatch (cause: 1) ---
    case("rej-r2-mk03", ["media-kit-studio"],
         "mk03 shell: build the pilot kit → lead",
         {"workspace/flows/media-kit-studio/mk03-shell/cycle.md":
          cyc("ready — BRIEF complete (written by mk02's closing "
              "hand, 2026-10-27)")},   # status string verbatim, live
         False, "R2: 'BRIEF complete' is a phase, not a close"),

    # --- lines that self-record their state (cause: 3) ---
    case("rej-r5-a07-decided", ["calendar-app"],
         "a07 sync — decided at the chair 2026-10-30; build follows",
         {"workspace/flows/calendar-app/a07-sync/cycle.md":
          cyc("done")},
         False, "R5: the line's own segment says 'decided'"),
    case("rej-r5-prcrew-dated", ["pr-crew"],
         "2026-10-28 — c04 manual runs landed, evidence filed",
         {"workspace/flows/pr-crew/c04-runs/cycle.md": cyc("done")},
         False, "R5: a dated journal line carrying its state"),
    case("rej-r5-appraiser-passed", ["whole-idea-reimagined"],
         "w02 appraisal passed at the gate; shelf updated",
         {"workspace/flows/whole-idea-reimagined/w02-dig/cycle.md":
          cyc("done")},
         False, "R5: the line's own segment says 'passed'"),

    # --- an informed re-run on a closed cycle (cause: 1) ---
    case("rej-r5-dp01-rerun", ["docs-to-package"],
         "dp01 re-run knowingly after the close — the seat's line "
         "already knew",
         {"workspace/flows/docs-to-package/dp01-pack/cycle.md":
          cyc("done")},
         False, "R5: dispatched-knowingly is a self-state"),

    case("rej-r5-ruled", ["memory-bank"],
         "m03 contradiction ruled at this seat 2026-11-04; the "
         "follow-on does not proceed",
         {"workspace/flows/memory-bank/m03-implement/cycle.md":
          cyc("done")},
         False, "R5: 'ruled' is the decided-family's own word (the "
                "live fleet's post-calibration lines carry it)"),

    # --- positive controls: these MUST pair ---
    case("ctrl-path-closed", ["lane-c"],
         "prep — blocked-on: ~/workspace/flows/lane-c/c01-x/"
         "cycle.md → lead",
         {"workspace/flows/lane-c/c01-x/cycle.md": cyc("done")},
         True, "control: a path citation anchors to its own state"),
    case("ctrl-subcycle-exact", ["workspace-docs"],
         "a04.1 annex pass: still open → lead",
         {"workspace/flows/workspace-docs/a04.1-annex/cycle.md":
          cyc("done")},
         True, "control: exact-id resolution pairs when a04.1 "
               "itself is closed"),
    case("ctrl-packet-at-desk", ["devops"],
         "packet: 0003 @dev-desk — the display item still rides "
         "→ devops",
         {"skills/dev-desk/completed/0003-muse-call-display/"
          "REQUEST.md": "# the desk's own 0003\n"},
         True, "control: the desk is part of the citation"),
    case("ctrl-closed-deviation", ["lane-d"],
         "d05 polish: still on the queue → lead",
         {"workspace/flows/lane-d/d05-polish/cycle.md":
          cyc("closed-pass-with-deviation")},
         True, "control: 'closed-pass-with-deviation' is closed"),
    case("ctrl-presenting", ["memory-bank"],
         "m03-implement wave 3 WAITING on the review tap",
         {"workspace/flows/memory-bank/m03-implement/cycle.md":
          cyc("done")},
         True, "control: a presenting line with no self-state "
               "segment pairs"),
]


def main():
    compiler = os.path.join(HERE, "..", "board-compiler.py")
    if "--compiler" in sys.argv:
        compiler = sys.argv[sys.argv.index("--compiler") + 1]
    bc = load_compiler(os.path.abspath(compiler))
    work = os.path.join(HERE, "..", "_run", "corpus-work")
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)
    passed = failed = 0
    for c in CASES:
        root = os.path.join(work, c["name"])
        home = os.path.join(root, "home")
        for rel, text in c["files"].items():
            p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as fh:
                fh.write(text)
        records = bc.Records(os.path.join(root, "workspace"),
                             [os.path.join(root, "skills")], home=home)
        lane = bc.Lane("corpus-lane")
        lane.flows = c["flows"]
        band = bc.Band(f"## NEXT\n- {c['line']}\n", "corpus")
        pairs, _, _ = bc.c7_pairs(records, lane, band, None)
        got = bool(pairs)
        ok = got == c["expect_pair"]
        passed += ok
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {c['name']} — "
              f"expected {'pair' if c['expect_pair'] else 'no pair'}"
              f", got {'pair' if got else 'no pair'} · {c['cause']}")
    print(f"\n{passed}/{passed + failed} corpus cases grade as "
          f"expected (16 calibration-verdict fixtures + 5 controls)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
