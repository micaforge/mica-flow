#!/usr/bin/env python3
"""The needs-compiler battery (packet 0020, PLAN SS10 — the
done-when checks, each failing for its OWN reason).

Forward battery: the compiler runs against the synthetic
fixture (needs_fixture.py) — a joint --write lands both boards
in one commit; the needs board's rows resolve, bind checker
states by the STATE-line citation (Q5), withhold the excluded
pointer byte-level (SS10.3), refuse the double designation
without parsing a row (SS10.1), reject the self-certifying
block (SS10.2a), let no prose mint a state (SS10.2b), read a
stale refresh unknown, and compile the fold fixture's corpus
in agreement with the seed checker (SS10.4 — parse-level
verdicts + findings compared directly).

Break battery (the proof the forward battery can fail): two
scratch COPIES of the compiler — (1) the state-smuggling scan
removed, (2) the pointer gate removed — must MISS the smuggle
and LEAK the withheld pointer respectively. A battery that
passes both ways proves nothing and does not ship.

Run: python3 needs_battery.py [--keep]
Exit 0 iff every forward assertion passes AND both break
variants misbehave as required.
"""
import importlib.machinery
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import needs_fixture as fx  # noqa: E402

COMPILER = os.path.join(HERE, "..", "needs-compiler.py")
SIBLING = os.path.join(HERE, "..", "board-compiler.py")
FIXTURE_HOME = os.path.expanduser(
    "~/workspace/projects/micaforge/repos/estate-template/"
    "workshop/flows/_template")
SEED_CHECK = os.path.join(FIXTURE_HOME, "needs-index-fixture",
                          "check_needs_index.py")
ROOT = os.path.join(HERE, "_run", "needs-fixture")

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}"
          + (f" — {detail}" if detail and not cond else ""))


def run_compiler(root, *args, compiler=COMPILER):
    return subprocess.run(
        [sys.executable, compiler, "--repo", root,
         "--workspace-root", os.path.join(root, "workspace"),
         "--desks-root", os.path.join(root, "skills"), *args],
        capture_output=True, text=True)


def load_module(path, name):
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def row_line(board, project, rid):
    """The rendered board line for (project section, row id)."""
    in_section = False
    for ln in board.splitlines():
        if ln.startswith("## "):
            in_section = project in ln
            continue
        if in_section and ln.startswith(f"- {rid} "):
            return ln
    return ""


def main():
    keep = "--keep" in sys.argv
    samples, targets = {}, {}
    sdir = os.path.join(FIXTURE_HOME, "needs-index-fixture",
                        "samples")
    tdir = os.path.join(FIXTURE_HOME, "needs-index-fixture",
                        "targets")
    for fn in sorted(os.listdir(sdir)):
        samples[fn] = open(os.path.join(sdir, fn)).read()
    for fn in sorted(os.listdir(tdir)):
        targets[fn] = open(os.path.join(tdir, fn)).read()
    template_text = open(os.path.join(FIXTURE_HOME,
                                      "AGENT.md")).read()

    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    info = fx.seed(ROOT, samples, targets, template_text)
    fx.seed_packets(ROOT)

    # ---------- the first joint write ----------
    r = run_compiler(ROOT, "--write")
    check("first --write exits 0", r.returncode == 0,
          r.stdout + r.stderr)
    head_after = subprocess.run(
        ["git", "-C", ROOT, "rev-parse", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    last = subprocess.run(
        ["git", "-C", ROOT, "log", "-1", "--name-only",
         "--format=%s"], capture_output=True, text=True).stdout
    check("one commit lands both board pairs",
          "memory/board/BOARD.md" in last
          and "memory/board/NEEDS.md" in last
          and "memory/board/needs-ledger.jsonl" in last
          and "memory/board/ping-ledger.jsonl" in last,
          last)
    board_path = os.path.join(ROOT, "memory", "board",
                              "NEEDS.md")
    board = open(board_path).read()
    ledger = open(os.path.join(
        ROOT, "memory", "board", "needs-ledger.jsonl")).read()
    check("coverage is stated on the board's face",
          re.search(r"coverage: indexed \d+/\d+ projects · "
                    r"rows resolved \d+ · unknown \d+", board)
          is not None)

    # ---------- SS10.1: two designated indexes ----------
    check("double designation is a finding naming both paths",
          "double-designation" in board
          and "workspace/flows/betaflow/AGENT.md" in board
          and "workspace/flows/betaflow/sub/AGENT.md" in board)
    check("no row from either beta index is parsed (C3)",
          fx.BETA_CANARY not in board
          and row_line(board, "betaflow", "boundary-current")
          == "")
    rc = run_compiler(ROOT, "--check")
    check("--check exits 1 on the fixture's findings",
          rc.returncode == 1, rc.stdout)
    check("--check names the double designation",
          "double-designation" in rc.stdout)

    # ---------- alphaflow: resolution + checker binding ----------
    ln = row_line(board, "alphaflow", "boundary-current")
    check("alpha boundary resolves", "→ resolved" in ln, ln)
    check("alpha boundary claimed via the packet's STATE-line",
          "state: claimed" in ln
          and "packet @ dev-desk/in-progress/9001-fixture" in ln,
          ln)
    ln = row_line(board, "alphaflow", "visual-face")
    check("alpha visual-face checked via STATE-line",
          "→ resolved" in ln and "state: checked" in ln, ln)
    ln = row_line(board, "alphaflow", "template-conformance")
    check("alpha conformance verified via STATE-line",
          "state: verified" in ln, ln)
    ln = row_line(board, "alphaflow", "floors-registered")
    check("alpha floors resolve on the registry entry + assert",
          "→ resolved" in ln and "floor-assert" in ln, ln)
    ln = row_line(board, "alphaflow", "business-gap-line")
    check("alpha business-gap resolves on its State line",
          "→ resolved" in ln, ln)
    ln = row_line(board, "alphaflow", "ladder-rungs")
    check("alpha ladder-rungs unassessed -> unknown",
          "→ unknown" in ln and "unassessed" in ln, ln)

    # ---------- SS10.2: self-certification, both points ----------
    check("self-certifying charter rejected at parse",
          "state-smuggling" in board
          and "state-smuggling" in rc.stdout)
    ln = row_line(board, "epsilonflow", "tests-break-evidence")
    check("target prose mints no state (the board-level twin)",
          "state: pending" in ln
          and "state: verified" not in ln
          and "checker:" not in ln, ln)
    row_ids = ("boundary-current", "template-conformance",
               "visual-face", "business-gap-line",
               "floors-registered", "tests-break-evidence",
               "ladder-rungs", "production-bar-axes",
               "provenance-current", "privacy-law-held")
    bad_vocab = [l for l in board.splitlines()
                 if any(l.startswith(f"- {i} ·")
                        for i in row_ids)
                 and re.search(r"state: (verified|checked|graded"
                               r"|claimed)", l)
                 and "checker:" not in l]
    check("vocabulary invariant: no projected row carries a "
          "work state without its checker citation on the line",
          not bad_vocab, str(bad_vocab[:2]))

    # ---------- the failed-check pair ----------
    ln = row_line(board, "epsilonflow", "visual-face")
    check("failed STATE-line returns the row to pending, "
          "paired", "state: pending" in ln and "⚠ pair" in ln,
          ln)
    check("--check surfaces the pair",
          "pair:" in rc.stdout and "visual-face" in rc.stdout)

    # ---------- SS10.3: pointer into an excluded home ----------
    ln = row_line(board, "zetaflow", "boundary-current")
    check("excluded pointer renders pointer-withheld",
          "pointer-withheld" in ln
          or "pointer withheld" in ln, ln)
    check("byte-level non-carriage: the pointer string, the "
          "canary, and the target's timing ride NO output",
          "../vaultflow/secret-record.md" not in board
          and fx.CANARY not in board
          and fx.CANARY not in ledger
          and "workspace/flows/vaultflow" not in board)
    check("the excluded target was never opened (mtime "
          "survives)", os.path.getmtime(info["secret"])
          == info["secret_mtime"])
    check("the excluded home renders nowhere on the board",
          "vaultflow" not in board)

    # ---------- staleness + unindexed ----------
    ln = row_line(board, "thetaflow", "boundary-current")
    check("stale refresh reads unknown (stale), never failed",
          "→ unknown" in ln and "(stale)" in ln, ln)
    check("unindexed project renders as a state line",
          "state: unindexed" in board
          and "gammaflow" in board)

    # ---------- no-op discipline ----------
    r2 = run_compiler(ROOT, "--write")
    head2 = subprocess.run(
        ["git", "-C", ROOT, "rev-parse", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    check("second --write is a no-op (HEAD unmoved)",
          r2.returncode == 0 and head2 == head_after,
          r2.stdout + r2.stderr)

    # ---------- SS10.4: agreement with the seed checker ----------
    nc = load_module(COMPILER, "needs_compiler_battery")
    repo = nc.load_sibling().Repo(ROOT)
    head = repo.head()
    tree = repo.ls_tree(head)
    agree = True
    detail = ""
    for name in sorted(samples):
        slug = "corpus-" + name[:-3]
        cpath = f"workspace/flows/{slug}/AGENT.md"
        text = open(os.path.join(ROOT, cpath)).read()
        rows, findings, has = nc.parse_index_block(text)
        states = nc.parse_level_states(rows, cpath, tree, ROOT)
        seed = subprocess.run(
            [sys.executable, SEED_CHECK,
             os.path.join(sdir, name)],
            capture_output=True, text=True)
        seed_findings = sorted(
            ln[len("FINDING: "):] for ln in
            seed.stdout.splitlines()
            if ln.startswith("FINDING: "))
        if sorted(findings) != seed_findings:
            agree = False
            detail = (f"{name}: findings differ — build "
                      f"{sorted(findings)} vs seed "
                      f"{seed_findings}")
            break
        seed_states = {}
        for ln in seed.stdout.splitlines():
            m = re.match(r"\s+([a-z0-9-]+): (declared|unknown)"
                         r"\b", ln)
            if m:
                seed_states[m.group(1)] = m.group(2)
        if states != seed_states:
            agree = False
            detail = (f"{name}: states differ — build {states}"
                      f" vs seed {seed_states}")
            break
    check("build parser agrees with the seed checker on the "
          "whole fold corpus (findings + per-row verdicts)",
          agree, detail)
    rows, findings, has = nc.parse_index_block(template_text)
    states = nc.parse_level_states(rows, "AGENT.md", tree, ROOT)
    check("the folded template itself parses: ten rows, all "
          "unknown, no findings (the gate's own shape)",
          has and len(rows) == 10 and not findings
          and set(states.values()) == {"unknown"},
          f"{len(rows)} rows, findings={findings}")

    # ---------- break battery ----------
    src = open(COMPILER).read()
    bdir = os.path.join(HERE, "_run", "break-variants")
    os.makedirs(bdir, exist_ok=True)
    shutil.copy(SIBLING, os.path.join(bdir,
                                      "board-compiler.py"))
    # (1) the state-smuggling scan removed
    needle = 'STATE_WORDS = ("checked", "verified", "graded", ' \
             '"claimed",\n               "pending")'
    assert needle in src, "smuggling-scan needle not found"
    v1 = os.path.join(bdir, "no-smuggling-scan.py")
    with open(v1, "w") as fh:
        fh.write(src.replace(needle, "STATE_WORDS = ()"))
    mod = load_module(v1, "needs_variant_noscan")
    _rows, vfindings, _has = mod.parse_index_block(
        samples["self-certifying.md"])
    check("BREAK (1): without the smuggling scan the variant "
          "MISSES the smuggled state — the real scan is what "
          "catches it",
          not any("state-smuggling" in f for f in vfindings),
          str(vfindings))
    # (2) the pointer gate removed
    needle2 = "def path_excluded(rel, prefs):\n"
    assert needle2 in src, "gate needle not found"
    v2 = os.path.join(bdir, "no-pointer-gate.py")
    with open(v2, "w") as fh:
        fh.write(src.replace(
            needle2,
            needle2 + "    return False  # BREAK VARIANT\n",
            1))
    rv = run_compiler(ROOT, "--render", compiler=v2)
    check("BREAK (2): without the pointer gate the variant "
          "LEAKS the withheld pointer onto its board",
          "../vaultflow/secret-record.md" in rv.stdout,
          rv.stdout[:200] + rv.stderr[:200])

    if not keep:
        pass  # the fixture stays under _run for inspection
    passed = sum(1 for _n, ok in RESULTS if ok)
    verdict = "ALL PASS" if passed == len(RESULTS) else "FAILED"
    print(f"\nBATTERY: {verdict} ({passed}/{len(RESULTS)})")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
