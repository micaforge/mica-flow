#!/usr/bin/env python3
"""The scan-guard battery for packet 0018: the board compiler's
--write path runs the memory sweep's OWN secret-scan patterns over
the composed board + ledger before the commit, failing closed.

Proofs:
  SOURCING — the compiler imports its patterns live from the
  sweep's implementation (~/workspace/bin/memory-commit-sweep):
  the loaded (name, regex) set IS the sweep's SECRET_PATTERNS, the
  compiler file carries no literal copy of the sweep's regexes,
  and scan verdicts agree with the sweep's own scan_text on a
  sample set (parity).
  REFUSAL — a fixture lane whose queue line plants an AWS-shaped
  key: --write refuses (exit 1), names the file + the pattern
  class, never prints the value, HEAD unchanged, no board file
  written anywhere. The SAME fixture with the plant removed
  compiles and commits normally.
  CONTROL — a plant matching a sweep pattern a hand-rolled list
  would plausibly miss (github_pat_, the fine-grained PAT prefix
  in the sweep's github-token class) still refuses — the guard is
  the sweep's set, not a generic list.
  LEDGER — the scan covers the composed ledger bytes, not only
  the board (unit-level, via scan_composed).
  UNLOADABLE — when the sweep source itself cannot be loaded
  (missing file · empty pattern set · unparseable source),
  --write refuses (exit 1, no commit) rather than commit
  unscanned. Mechanism: SWEEP_PATH is derived from the
  compiler's HOME (os.path.expanduser("~")), so each shape is
  exercised end-to-end by running the real CLI as a subprocess
  with HOME staged to a directory whose
  workspace/bin/memory-commit-sweep is absent / empty /
  syntactically broken. No production-code override hook was
  added for this — the env is the seam the code already has.
  ALERT (packet 0019) — every refusal also writes the
  sweep-alert.json shape to <workspace>/data/lane/
  board-alert.json (the workspace under compile, so fixtures
  are hermetic): a hit's alert carries the flagged file +
  pattern class, a load failure's carries the cause in
  "error", the value is absent from the alert, a clean
  compile unlinks the alert (the sweep's lifecycle), and an
  alert write that itself fails (the alert dir pre-created
  as a plain file) leaves the refusal intact.

Run: python3 scan_test.py [--compiler PATH] [--keep]
Exit 0 iff every assertion passes.
"""
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_fixture as fx  # noqa: E402

RESULTS = []

AWS_PLANT = "AKIAIOSFODNN7EXAMPLE"          # sweep class: aws-access-key
PAT_PLANT = "github_pat_" + "A1b2C3d4E5f6G7h8I9j0K1L2M3N4"  # github-token
APIKEY_PLANT = "sk-" + "A1b2C3d4E5f6G7h8I9j0K1L2M3N4O5P6Q7"  # api-key
ALPHA = fx.A


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}"
          + (f" — {detail}" if detail and not cond else ""))


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def run_compiler(compiler, root, *args, env=None):
    r = subprocess.run(
        [sys.executable, compiler, "--repo", root,
         "--workspace-root", os.path.join(root, "workspace"),
         "--desks-root", os.path.join(root, "skills"), *args],
        capture_output=True, text=True, env=env)
    return r


def alert_path(root):
    return os.path.join(root, "workspace", "data", "lane",
                        "board-alert.json")


def read_alert(root):
    """(raw_text, parsed) or (None, None) when no alert exists."""
    p = alert_path(root)
    if not os.path.exists(p):
        return None, None
    with open(p) as f:
        raw = f.read()
    try:
        return raw, json.loads(raw)
    except Exception:
        return raw, None


def head_of(root):
    return subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def tree_paths(root):
    out = subprocess.run(["git", "-C", root, "ls-tree", "-r",
                          "--name-only", "HEAD"],
                         capture_output=True, text=True).stdout
    return set(out.splitlines())


def alpha_with(root, extra_item):
    items = ["alpha item one: build the widget → alpha",
             "alpha item two: review the plan"]
    if extra_item:
        items.append(extra_item)
    fx.put(root, f"side-chats/{ALPHA}/LANE_MEMORY.md",
           fx.band("alpha", items,
                   ["2026-11-03 — alpha seeded the fixture"]))


def sourcing_checks(compiler):
    comp = load_module("board_compiler_under_test", compiler)
    sweep = load_module("memory_commit_sweep_source",
                        os.path.expanduser(
                            "~/workspace/bin/memory-commit-sweep"))
    loaded = [(n, p.pattern) for n, p in comp.load_sweep_patterns()]
    source = [(n, p.pattern) for n, p in sweep.SECRET_PATTERNS]
    check("sourcing: loaded set IS the sweep's SECRET_PATTERNS",
          loaded == source and len(loaded) == 5,
          f"loaded={loaded!r}")
    check("sourcing: SWEEP_PATH names the sweep implementation",
          comp.SWEEP_PATH.endswith("workspace/bin/memory-commit-sweep"))
    text = open(compiler).read()
    check("sourcing: no literal copy of the sweep's regexes in the "
          "compiler", "AKIA[0-9A-Z]" not in text
          and "ghp|gho" not in text
          and "xox[baprs]" not in text
          and "credential-assignment" not in text)
    # parity: the compiler's verdict == the sweep's scan_text verdict
    samples = ["a clean queue line, nothing to see",
               f"key {AWS_PLANT} inside",
               f"pat {PAT_PLANT} inside",
               f"sample {APIKEY_PLANT} trailing",
               "token: abcdefghijklmnop1234",
               "-----BEGIN RSA PRIVATE KEY-----"]
    parity = all(
        bool(comp.scan_composed(s, "")) ==
        (sweep.scan_text(s) is not None) for s in samples)
    check("sourcing: verdict parity with the sweep's scan_text on "
          "6 samples", parity)
    # the api-key sample really exercises the api-key class (the
    # one class the original 5 samples omitted): both the sweep's
    # scan_text and the compiler's scan name it, and nothing else
    apikey_sample = f"sample {APIKEY_PLANT} trailing"
    check("sourcing: the api-key sample is an api-key hit for both "
          "the sweep and the compiler",
          sweep.scan_text(apikey_sample) == "api-key"
          and comp.scan_composed(apikey_sample, "") ==
          [(comp.BOARD_PATH, "api-key")])
    hits = comp.scan_composed("clean board",
                              f'{{"item": "key {AWS_PLANT}"}}')
    check("ledger: a plant in the composed ledger is caught, "
          "ledger path + class named",
          hits == [(comp.LEDGER_PATH, "aws-access-key")],
          f"hits={hits!r}")
    check("ledger: the finding never carries the matched value",
          AWS_PLANT not in json.dumps(hits))
    return comp


def fixture_checks(compiler, workdir):
    # --- refusal: plant in alpha's queue, first compile ever ---
    root = os.path.join(workdir, "fx-refuse")
    fx.seed(root)
    alpha_with(root, f"alpha item three: rotate the key {AWS_PLANT}"
                     " → alpha")
    fx.commit(root, "plant: alpha queue carries a key-shaped string")
    h1 = head_of(root)
    r = run_compiler(compiler, root, "--write")
    out = (r.stdout or "") + (r.stderr or "")
    check("refusal: --write exits non-zero on the plant",
          r.returncode == 1, f"rc={r.returncode} out={out[:200]}")
    check("refusal: finding names the board file + pattern class",
          "memory/board/BOARD.md" in out
          and "aws-access-key" in out, out[:240])
    check("refusal: the planted value is never printed",
          AWS_PLANT not in out)
    check("refusal: HEAD unchanged (no commit landed)",
          head_of(root) == h1)
    check("refusal: no board file in the tree or the worktree",
          "memory/board/BOARD.md" not in tree_paths(root)
          and not os.path.exists(
              os.path.join(root, "memory", "board", "BOARD.md")))
    # --- packet 0019: the refusal leaves the alert record ---
    raw, alert = read_alert(root)
    check("alert: the refusal writes the alert record in the "
          "sweep's shape (ts + flagged file/pattern)",
          alert is not None
          and "ts" in alert
          and alert.get("flagged") == [
              {"file": "memory/board/BOARD.md",
               "pattern": "aws-access-key"}],
          f"alert={raw!r}")
    check("alert: the planted value is absent from the alert",
          raw is not None and AWS_PLANT not in raw)
    # --- same fixture, plant removed: compiles + commits ---
    alpha_with(root, None)
    fx.commit(root, "unplant: the key-shaped string is gone")
    r = run_compiler(compiler, root, "--write", "--json")
    ok = r.returncode == 0
    landed = ok and "memory/board/BOARD.md" in tree_paths(root)
    board = ""
    if landed:
        board = subprocess.run(
            ["git", "-C", root, "show", "HEAD:memory/board/BOARD.md"],
            capture_output=True, text=True).stdout
    check("recovery: the same fixture without the plant compiles "
          "and commits", bool(landed), f"rc={r.returncode}")
    check("recovery: the landed board is clean + scan reported",
          AWS_PLANT not in board
          and json.loads(r.stdout).get("scan", {}).get("hits") == 0)
    check("alert: the clean compile unlinks the alert (the "
          "sweep's lifecycle — present only while eyes are needed)",
          not os.path.exists(alert_path(root)))
    # --- control: the github_pat_ plant (sweep-set proof) ---
    root2 = os.path.join(workdir, "fx-control")
    fx.seed(root2)
    alpha_with(root2, f"alpha item three: file the pat {PAT_PLANT}"
                      " → alpha")
    fx.commit(root2, "plant: alpha queue carries a pat-shaped string")
    h2 = head_of(root2)
    r = run_compiler(compiler, root2, "--write")
    out = (r.stdout or "") + (r.stderr or "")
    check("control: github_pat_ plant refuses (the sweep's set, "
          "not a generic list)",
          r.returncode == 1 and "github-token" in out
          and head_of(root2) == h2, f"rc={r.returncode} out={out[:200]}")
    check("control: the pat value is never printed",
          PAT_PLANT not in out)
    raw, alert = read_alert(root2)
    check("alert (control): the github_pat_ refusal alerts with "
          "class github-token, the value absent from the alert",
          alert is not None
          and alert.get("flagged") == [
              {"file": "memory/board/BOARD.md",
               "pattern": "github-token"}]
          and raw is not None and PAT_PLANT not in raw,
          f"alert={raw!r}")


def unloadable_checks(compiler, workdir):
    # The guard must fail closed on its own source: a compiler
    # that cannot load the sweep's patterns must not commit.
    # SWEEP_PATH derives from HOME, so each broken shape is
    # staged as a HOME whose workspace/bin/memory-commit-sweep
    # is absent / carries an empty pattern set / does not parse,
    # and the real CLI is run against a CLEAN fixture repo (no
    # plant — the refusal can only be the guard's own failure).
    shapes = [("missing", None),
              ("empty", "SECRET_PATTERNS = []\n"),
              ("unparseable", "SECRET_PATTERNS = [(\n"
                              "not python at all\n")]
    for shape, sweep_text in shapes:
        root = os.path.join(workdir, f"fx-unloadable-{shape}")
        fx.seed(root)  # the seed commit IS the clean fixture
        h = head_of(root)
        home = os.path.join(workdir, f"home-{shape}")
        bindir = os.path.join(home, "workspace", "bin")
        os.makedirs(bindir)
        if sweep_text is not None:
            with open(os.path.join(bindir, "memory-commit-sweep"),
                      "w") as f:
                f.write(sweep_text)
        env = dict(os.environ, HOME=home)
        r = run_compiler(compiler, root, "--write", env=env)
        out = (r.stdout or "") + (r.stderr or "")
        check(f"unloadable ({shape}): --write exits 1 naming the "
              f"guard's load failure",
              r.returncode == 1
              and "cannot load the sweep" in out,
              f"rc={r.returncode} out={out[:240]}")
        check(f"unloadable ({shape}): HEAD unchanged, no board "
              f"file written",
              head_of(root) == h
              and "memory/board/BOARD.md" not in tree_paths(root)
              and not os.path.exists(
                  os.path.join(root, "memory", "board",
                               "BOARD.md")))
        raw, alert = read_alert(root)
        check(f"alert (unloadable {shape}): the refusal alerts "
              f"with the load cause in error, flagged empty",
              alert is not None
              and "cannot load the sweep" in
              str(alert.get("error", ""))
              and alert.get("flagged") == [],
              f"alert={raw!r}")


def alert_unwritable_checks(compiler, workdir):
    # Packet 0019: the alert write sits AFTER the refusal
    # decision and can never weaken it. Sabotage: the alert's
    # parent path (workspace/data/lane) pre-created as a plain
    # FILE, so the alert write must fail — the scan refusal
    # itself (AWS plant in alpha's queue) must stand untouched:
    # exit 1, no commit, the failure noted on stderr.
    root = os.path.join(workdir, "fx-alert-unwritable")
    fx.seed(root)
    alpha_with(root, f"alpha item three: rotate the key {AWS_PLANT}"
                     " → alpha")
    fx.commit(root, "plant: alpha queue carries a key-shaped string")
    h = head_of(root)
    os.makedirs(os.path.join(root, "workspace", "data"))
    with open(os.path.join(root, "workspace", "data", "lane"),
              "w") as f:
        f.write("not a directory — the alert has nowhere to land\n")
    r = run_compiler(compiler, root, "--write")
    out = (r.stdout or "") + (r.stderr or "")
    check("alert-unwritable: the refusal stands (exit 1, "
          "HEAD unchanged, no board written)",
          r.returncode == 1
          and "secret-scan refusal" in out
          and head_of(root) == h
          and not os.path.exists(
              os.path.join(root, "memory", "board", "BOARD.md")),
          f"rc={r.returncode} out={out[:240]}")
    check("alert-unwritable: the failed alert write is noted, "
          "never silent",
          "refusal alert write failed" in out
          and "the refusal stands" in out, out[:240])


def main():
    args = sys.argv[1:]
    compiler = os.path.join(HERE, "..", "board-compiler.py")
    keep = "--keep" in args
    if "--compiler" in args:
        compiler = args[args.index("--compiler") + 1]
    compiler = os.path.abspath(compiler)
    sourcing_checks(compiler)
    workdir = os.path.join(HERE, "scan-work")
    shutil.rmtree(workdir, ignore_errors=True)
    os.makedirs(workdir)
    fixture_checks(compiler, workdir)
    unloadable_checks(compiler, workdir)
    alert_unwritable_checks(compiler, workdir)
    if not keep:
        shutil.rmtree(workdir, ignore_errors=True)
    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} scan-guard "
          f"checks pass" + (f" — FAILED: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
