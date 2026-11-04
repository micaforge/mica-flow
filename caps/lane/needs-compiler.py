#!/usr/bin/env python3
"""needs-compiler — the project-needs board compiler (dev-desk
packet 0020, Front Desk item 0004's build leg). One Python 3 file,
stdlib only. A sibling leg on the rolling board's machinery
(packet 0017): it shares board-compiler.py's primitives by
file-path import (Q8 at the plan gate — the 0018 sweep-import
precedent) and never edits them.

WHAT IT DOES
  For each project in the home tree, find its ONE designated
  project-needs charter index (gate conditions C1-C7: the
  charter DECLARES, other records prove; exactly one designated
  index per project, C3; pointers are addresses, not licences,
  C6), read its declared rows (the ten stable IDs of C4), and
  resolve each row against the record of record it points to.
  Project the work states (pending · claimed · checked ·
  verified · graded) ONLY from checker records that carry the
  ruled citation binding (plan gate Q5: a STATE-line of the form
  `needs: <item-id> = <state>` in a checker record bound to the
  project by home or by charter citation — prose mentions mint
  nothing). Render the projection as the NEEDS board, a sibling
  pair with the rolling board under memory/board/ (NEEDS.md +
  needs-ledger.jsonl, Q9). A missing row, blank field,
  unresolvable pointer, or stale refresh reads UNKNOWN — never
  satisfied, never failed (C2). A pointer into a home excluded
  by its own property marking renders pointer-withheld: no
  content, summary, timing, or the pointer string itself rides
  any output (C6).

MODES
  --write    THE single writer pass for BOTH boards (plan gate
             Q4: one writer pass — one flock, one commit): under
             the rolling board's own writer lock, compose the
             sibling board from board-compiler's primitives and
             the needs board from this leg, scan all four composed
             files with the sweep's secret-scan patterns
             (imported live, packets 0018/0019 — a hit refuses
             the whole commit and leaves the refusal alert), land
             them in ONE commit touching only memory/board/**,
             and verify both boards' stamps read back at HEAD.
             Lock held -> the whole pass defers (exit 0, one
             line). The compiler never pushes.
  --render   read-only: render the NEEDS board at HEAD to stdout
             (or --out FILE). Never commits, takes no lock.
  --check    the checker leg (read-only): double designation ·
             parse findings · bare `no` · failed-check pairs.
             Unknowns are counted, never failed on (C2).
             Exit 1 if any finding exists, else 0.

OPTIONS
  --repo PATH        the home/memory repo (default ~).
  --workspace-root   where cited records live on disk
                     (default <repo>/workspace).
  --desks-root       desk packages root for packet records
                     (default ~/skills, /opt/muse/skills scanned).
  --out FILE         --render output file instead of stdout.
  --json             machine mode: one object, never truncated.
  --more             full listing where the brief truncates.
  --help             this surface; exits 0.

THE LAW IT RUNS UNDER (gate ruling C1-C7 + the 0020 plan gate)
  - Census scope at v1 is the HOME TREE only (Q2): AGENT.md
    charters under workspace/flows/** and workspace/projects/**,
    enumerated by charter-home shape at fixed depths (the
    projects tree is ~20 GB — a recursive crawl is minutes;
    enumerate_charter_paths names the shapes).
    READ POSTURE, corrected at build on a discovered fact:
    the home (memory) repo is an allowlist repo — it tracks
    LANE_MEMORY-class records and the board pairs, NOT the
    charters (AGENT.md is git-ignored there), so charters and
    the records rows cite are read PRESENT-STATE from disk,
    exactly the sibling's posture for cited records ("the
    repo governs lanes + inclusion; the records a queue cites
    are present-state"). The board pair, the stamp, and the
    interval discipline stay anchored to the memory repo at
    HEAD, like the sibling's. Project grouping is by the
    project ROOT (Q1): the designated charter's containing
    project home — the nearest ancestor carrying BOUNDARY.md,
    falling back to the flow dir / the top projects/ dir.
    points-to attributes a charter to the project its pointer
    names. Cross-root duplicates are a named v1 limit: without
    a project key, two designated charters in DIFFERENT roots
    read as two projects; two under ONE root are the C3
    finding.
  - Staleness is event-relative, one rule for all IDs (Q3): a
    row is stale when the project root's newest record event
    postdates (by date) the row's refreshed_at date. Under
    the disk posture the event evidence is the root's newest
    file mtime (day granularity; the git history of the
    allowlist repo carries no charter events at all). A blank
    refreshed_at reads unknown (C2).
  - floors-registered resolves on Q10's widened criteria as
    amended (the codable form): the registry entry resolves for
    the depended-on service/unit/cron/hook/tool the pointer
    names + floor asserts PASS. The registry-wide criteria
    behind the entry (the automation registry's own check, CLI
    contract checks, vault-only secrets, failure signatures)
    are the owning seats' records compiled INTO the registry
    this leg reads; the leg does not re-derive them (C4: no
    criterion enters through this implementation that is not
    in the compilation or the law it points to).
  - Inclusion-by-property governs every read (C6): the
    excluded-prefix set is built (lanes INDEX resolution +
    the property marking's carrier files, answered by
    `git grep -l` — paths only) BEFORE any file opens; bytes
    of an excluded home never enter this tool.
  - The leg never grades: conformance grades, Judge verdicts
    and gate PASSes are READ from their records, never
    computed here. A `graded` STATE-line mints only from a
    grader's own home (the Judge lane · the gate bench ·
    the conformance programme · a completed desk packet).

EXIT CODES: 0 ok (incl. lock-deferred) · 1 failure/findings ·
2 usage.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

os.environ["GIT_OPTIONAL_LOCKS"] = "0"

HOME = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
NEEDS_PATH = "memory/board/NEEDS.md"
NEEDS_LEDGER_PATH = "memory/board/needs-ledger.jsonl"
BOARD_SUBTREE = "memory/board/"
JUDGE_HOME = "workspace/flows/judge"   # compilation SS1: the
# Judge lane's home — the only home whose records can resolve
# or grade production-bar-axes.

TEN_IDS = [
    "boundary-current", "template-conformance", "visual-face",
    "business-gap-line", "floors-registered", "tests-break-evidence",
    "ladder-rungs", "production-bar-axes", "provenance-current",
    "privacy-law-held",
]
# checker field + claim pool per item (the codable form). The
# desk SECTION a pending row renders under is derived from the
# pool/checker: the free-claim pool is the mechanical class.
ITEM_META = {
    "boundary-current":     {"checker": "any-desk",
                             "pool": "free-claim",
                             "section": "free-claim pool (any desk)"},
    "template-conformance": {"checker": "dev-desk-adoption-packets",
                             "pool": "single-home",
                             "section": "dev-desk"},
    "visual-face":          {"checker": "programme-census",
                             "pool": "free-claim",
                             "section": "free-claim pool (any desk)"},
    "business-gap-line":    {"checker": "closing-seat",
                             "pool": "free-claim",
                             "section": "free-claim pool (any desk)"},
    "floors-registered":    {"checker": "platform-audit-or-devops",
                             "pool": "free-claim",
                             "section": "free-claim pool (any desk)"},
    "tests-break-evidence": {"checker": "building-desk",
                             "pool": "single-home",
                             "section": "dev-desk"},
    "ladder-rungs":         {"checker": "crew-adversary",
                             "pool": "single-home",
                             "section": "crew-adversary"},
    "production-bar-axes":  {"checker": "judge-lane",
                             "pool": "single-home",
                             "section": "judge-lane"},
    "provenance-current":   {"checker": "closing-seat",
                             "pool": "single-home",
                             "section": "closing-seat"},
    "privacy-law-held":     {"checker": "any-desk-on-sight",
                             "pool": "single-home",
                             "section": "any-desk-on-sight"},
}
SECTION_ORDER = ["free-claim pool (any desk)", "dev-desk",
                 "judge-lane", "closing-seat", "crew-adversary",
                 "any-desk-on-sight"]
WORK_STATES = ("pending", "claimed", "checked", "verified",
               "graded")
STATE_RANK = {s: i for i, s in enumerate(WORK_STATES)}
NEEDS_LINE = re.compile(
    r"^needs:\s*([a-z0-9][a-z0-9\-]*)\s*=\s*([a-z]+)\s*$", re.M)
ROW_RE = re.compile(
    r"^- ([a-z0-9-]+) · applies: (\S+)"
    r" · evidence: (.+?) · refreshed_at: (.+)$")
STATE_WORDS = ("checked", "verified", "graded", "claimed",
               "pending")
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

JSON_MODE = False
BC = None   # board-compiler, imported by file path (Q8)


def fail(msg, code=1):
    if JSON_MODE:
        print(json.dumps({"error": msg}))
    else:
        print(f"needs-compiler: {msg}", file=sys.stderr)
    sys.exit(code)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_sibling():
    """board-compiler.py imported by file path (Q8's ruling;
    the 0018 sweep import is the in-family precedent). The
    sibling is import-guarded (main runs only as __main__)."""
    global BC
    if BC is not None:
        return BC
    import importlib.machinery
    import importlib.util
    path = os.path.join(HERE, "board-compiler.py")
    loader = importlib.machinery.SourceFileLoader(
        "board_compiler", path)
    spec = importlib.util.spec_from_loader("board_compiler",
                                           loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    BC = mod
    return BC


# ------------------------------------------------------------------
# inclusion (C6): the excluded-prefix set, built from properties
# BEFORE any file opens — the lanes INDEX resolution (the
# sibling's) plus every carrier file of the property marking,
# answered by `git grep -l` (paths only; no content read).
# ------------------------------------------------------------------

PRUNE_DIRS = {"node_modules", ".git", ".scratch", ".venv",
              "dist", "build", "vendor", "target", "__pycache__"}


def enumerate_charter_paths(workspace_root, repo_root):
    """Candidate charter paths (repo-relative), enumerated by
    charter-home SHAPE at fixed depths — never a recursive
    crawl (the projects tree is ~20 GB; a crawl is minutes).
    v1 shapes: flows/<flow>/ + flows/<flow>/<unit>/ ·
    projects/<p>/ + projects/<p>/<sub>/ + the org-nested repo
    form projects/<org>/repos/<repo>/ (+ one level in)."""
    import glob as _glob
    pats = [("flows", "*"), ("flows", "*/*"),
            ("projects", "*"), ("projects", "*/*"),
            ("projects", "*/repos/*"),
            ("projects", "*/repos/*/*")]
    out = []
    for sub, pat in pats:
        for f in _glob.glob(os.path.join(workspace_root, sub,
                                         pat, "AGENT.md")):
            out.append(os.path.relpath(f, repo_root))
    return sorted(set(out))


def excluded_prefixes(repo, head, tree, workspace_root=None,
                      record_files=()):
    bc = load_sibling()
    all_lanes, _included = bc.resolve_inclusion(repo, head)
    prefs = set()
    for slug, lane in all_lanes.items():
        if lane.excluded:
            prefs |= bc.lane_home_prefixes(lane)
    r = repo.git("grep", "-l", "-F", "-e",
                 "doorway-scope: excluded", head, check=False)
    if r.returncode == 0:
        for p in r.stdout.splitlines():
            p = p.strip()
            if not p:
                continue
            if re.match(r"memory/lanes/[^/]+\.md$", p):
                continue   # a lane page: its lane's prefixes,
                # already carried by the INDEX resolution above
            d = os.path.dirname(p)
            if d:
                prefs.add(d + "/")
                prefs.add(d)      # exact-dir spelling too
    # disk homes: the charters are untracked in the home repo,
    # so a project home's own marking is answered from disk —
    # `grep -l` over the enumerated record files (the census
    # charters + their homes' LANE_MEMORYs), PATHS ONLY into
    # this tool (the prop_at posture: the property is answered
    # from the record path; excluded bytes never enter it)
    if record_files:
        files = [os.path.join(repo.root, f) for f in record_files
                 if os.path.isfile(os.path.join(repo.root, f))]
        for i in range(0, len(files), 200):
            r = subprocess.run(
                ["grep", "-l", "-F", "-e",
                 "doorway-scope: excluded", "--",
                 *files[i:i + 200]],
                capture_output=True, text=True)
            for p in r.stdout.splitlines():
                p = p.strip()
                if not p:
                    continue
                rel = os.path.relpath(p, repo.root)
                d = os.path.dirname(rel)
                if d:
                    prefs.add(d + "/")
                    prefs.add(d)
    return prefs, all_lanes


def path_excluded(rel, prefs):
    """rel spellings tested: the repo-relative path itself, its
    home-relative form, and its workspace-stripped form (the
    sibling's prefix set carries both spellings)."""
    if not rel:
        return False
    forms = {rel, "~/" + rel}
    if rel.startswith("workspace/"):
        forms.add(rel[len("workspace/"):])
    for pref in prefs:
        base = pref.rstrip("/")
        for f in forms:
            if f == base or f.startswith(base + "/"):
                return True
    return False


# ------------------------------------------------------------------
# census + designation (C3; Q1 grouping by project root; Q2 home
# tree only at v1)
# ------------------------------------------------------------------

def project_root_for(path, repo_root):
    """The project home containing a charter: the nearest
    ancestor directory (from the charter's own dir up) carrying
    BOUNDARY.md on disk; fallback: the flow dir under
    workspace/flows/, else the top dir under
    workspace/projects/."""
    d = os.path.dirname(path)
    fallback = None
    m = re.match(r"(workspace/flows/[^/]+)", path)
    if m:
        fallback = m.group(1)
    else:
        m = re.match(r"(workspace/projects/[^/]+)", path)
        if m:
            fallback = m.group(1)
    cur = d
    while cur and cur not in ("workspace", ""):
        if os.path.isfile(os.path.join(
                repo_root, cur, "BOUNDARY.md")):
            return cur
        if cur == fallback:
            break
        cur = os.path.dirname(cur)
    return fallback or d


def designation_of(text):
    """(kind, points_to): kind in designated | points-to | none,
    from the charter's frontmatter (the fold's marker)."""
    bc = load_sibling()
    fm = bc.parse_frontmatter(text)
    v = fm.get("project-needs-index", "").strip()
    if v.lower().startswith("designated"):
        return ("designated", None)
    pt = fm.get("points-to", "").strip().strip("`<>\"' ")
    if pt:
        return ("points-to", pt)
    return ("none", None)


class Charter:
    def __init__(self, path, kind, points_to):
        self.path = path
        self.kind = kind
        self.points_to = points_to
        self.root = None


def census(repo, tree, prefs, workspace_root, paths):
    """Group the enumerated candidate charters (paths from
    enumerate_charter_paths — names only, nothing opened yet)
    into projects, skipping — without opening — any charter
    under an excluded home. Grouping is by root (Q1);
    points-to charters attribute to the project their pointer
    names. Returns (projects, charters) where projects maps
    root -> {designated: [Charter], plain: [Charter],
             attributed: [Charter]}."""
    charters = []
    for p in sorted(paths):
        if path_excluded(p, prefs):
            continue              # never opened (C6)
        try:
            text = open(os.path.join(repo.root, p),
                        errors="replace").read()
        except OSError:
            continue
        kind, pt = designation_of(text)
        c = Charter(p, kind, pt)
        c.text = text
        charters.append(c)
    # attribute points-to first: resolve the pointer to its
    # designated charter (repo-relative normalisation); an
    # unresolvable pointer leaves the charter plain in its own
    # root (its project is unindexed there).
    by_path = {c.path: c for c in charters}
    for c in charters:
        c.root = project_root_for(c.path, repo.root)
    for c in charters:
        if c.kind == "points-to":
            tgt = normalize_pointer(c.points_to, c.path, tree,
                                    repo.root)
            tc = by_path.get(tgt[1]) if tgt and tgt[0] else None
            if tc is not None and tc.kind == "designated":
                c.attributed_to = tc
                c.root = tc.root
            else:
                c.attributed_to = None
        else:
            c.attributed_to = None
    projects = {}
    for c in charters:
        pr = projects.setdefault(c.root, {"designated": [],
                                          "plain": [],
                                          "attributed": []})
        if c.attributed_to is not None:
            pr["attributed"].append(c)
        elif c.kind == "designated":
            pr["designated"].append(c)
        else:
            pr["plain"].append(c)
    # a root that only attributes elsewhere is not its own
    # project (Q1: points-to attributes)
    for root in list(projects):
        pr = projects[root]
        if not pr["designated"] and not pr["plain"] \
                and pr["attributed"]:
            del projects[root]
    return projects, charters


def owning_seat(root, all_lanes):
    """The seat owning a project root, per the lanes INDEX
    (the lane whose flows list names the flow dir); None when
    the INDEX does not resolve it."""
    m = re.match(r"workspace/flows/([^/]+)", root)
    if m:
        flow = m.group(1)
        for slug, lane in all_lanes.items():
            if flow in lane.flows:
                return slug
    return None


# ------------------------------------------------------------------
# row parse — the fold fixture's checker is the contract's seed:
# its grammar + findings vocabulary are carried unchanged in
# semantics (PLAN SS4). Parse-level row states are exactly
# {declared, unknown}; no charter content mints a work state.
# ------------------------------------------------------------------

def parse_index_block(text):
    """-> (rows, findings, has_block). rows: id -> {applies,
    evidence, refreshed_at} (first occurrence wins, as the
    seed). findings: the seed's vocabulary, in the seed's
    order (smuggling scan first, row findings in line order,
    missing-ids last — bare-`no` with them, as the seed)."""
    m = re.search(r"<!-- needs-index:begin -->(.*?)"
                  r"<!-- needs-index:end -->", text, re.S)
    if not m:
        return {}, [], False
    block = m.group(1)
    findings = []
    for w in sorted(STATE_WORDS):
        if re.search(r"(state|status|verdict):\s*" + w, block) \
                or re.search(r"applies:\s*" + w + r"\b", block):
            findings.append(
                f"state-smuggling: '{w}' appears as charter "
                f"content; the charter cannot mint a work state")
    rows = {}
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        rm = ROW_RE.match(line)
        if not rm:
            findings.append(f"unparseable-row: {line[:60]}")
            continue
        rid, applies, evidence, refreshed = rm.groups()
        if rid in rows:
            findings.append(f"duplicate-id: {rid}")
            continue
        rows[rid] = {"applies": applies,
                     "evidence": evidence.strip(),
                     "refreshed_at": refreshed.strip()}
    for rid in TEN_IDS:
        if rid not in rows:
            findings.append(f"missing-id: {rid}")
    for rid, row in rows.items():
        if row["applies"] not in ("yes", "no", "unassessed"):
            findings.append(
                f"bad-applies: {rid} = '{row['applies']}'")
        if row["applies"] == "no" and row["evidence"] == "—":
            findings.append(
                f"no-without-basis: {rid} says 'no' with no "
                f"basis pointer")
    return rows, findings, True


def parse_level_states(rows, charter_path, tree, repo_root):
    """The seed's per-row verdict {declared, unknown}: declared
    iff the evidence pointer resolves (existence, relative to
    the charter — on disk, the seed's own read posture) — the
    conformance oracle's rule, kept so the battery can assert
    agreement (PLAN SS4)."""
    out = {}
    for rid, row in rows.items():
        ev = row["evidence"]
        if ev == "—":
            out[rid] = "unknown"
            continue
        cand = normalize_pointer(ev, charter_path, tree,
                                 repo_root)
        exists = cand and cand[2] and os.path.exists(cand[2])
        out[rid] = "declared" if exists else "unknown"
    return out


# ------------------------------------------------------------------
# pointers (C5 record-shape-neutral; C6 addresses, not licences)
# ------------------------------------------------------------------

def normalize_pointer(pointer, charter_path, tree, repo_root):
    """-> (resolved_bool, repo_rel_or_None, disk_path_or_None).
    Spellings accepted: ~/… · workspace/… · memory/… ·
    side-chats/… · flows/… (workspace-stripped) · paths relative
    to the charter's directory (the seed's posture) · absolute.
    An #anchor addresses a section and is stripped for the path
    test. Resolution = the path exists as a git object at HEAD
    or as a present-state file/folder on disk."""
    p = (pointer or "").strip().split("#")[0].strip()
    if not p or p == "—":
        return (False, None, None)
    repo_rel, disk = None, None
    if p.startswith("~/"):
        disk = os.path.join(HOME, p[2:])
        rel = os.path.relpath(disk, repo_root)
        if not rel.startswith(".."):
            repo_rel = rel
    elif p.startswith("/"):
        disk = p
        rel = os.path.relpath(disk, repo_root)
        if not rel.startswith(".."):
            repo_rel = rel
    elif p.startswith(("workspace/", "memory/", "side-chats/")):
        repo_rel = p
        disk = os.path.join(repo_root, p)
    elif p.startswith(("flows/", "projects/")):
        repo_rel = "workspace/" + p
        disk = os.path.join(repo_root, repo_rel)
    else:
        base = os.path.dirname(charter_path)
        joined = os.path.normpath(os.path.join(base, p))
        if joined.startswith(".."):
            return (False, None, None)
        repo_rel = joined
        disk = os.path.join(repo_root, joined)
    if repo_rel and repo_rel in tree:
        return (True, repo_rel, disk)
    if repo_rel and any(t.startswith(repo_rel.rstrip("/") + "/")
                        for t in tree):
        return (True, repo_rel, disk)      # a folder target (C5)
    if disk and (os.path.isfile(disk) or os.path.isdir(disk)):
        return (True, repo_rel, disk)
    return (False, repo_rel, disk)


def read_target(repo, head, cand):
    """The record of record's text, or None. Present-state
    from disk first (the posture of the module header); a
    tracked-only path falls back to the git object at HEAD.
    A folder target reads its index/README/STATE record.
    NEVER called for a withheld pointer — the gate runs
    first (C6)."""
    ok, repo_rel, disk = cand
    if not ok:
        return None
    if disk:
        if os.path.isfile(disk):
            try:
                return open(disk, errors="replace").read()
            except OSError:
                pass
        if os.path.isdir(disk):
            for name in ("INDEX.md", "README.md", "STATE.md",
                         "index.md"):
                p = os.path.join(disk, name)
                if os.path.isfile(p):
                    try:
                        return open(p, errors="replace").read()
                    except OSError:
                        continue
    if repo_rel:
        text = repo.show(head, repo_rel)
        if text is not None:
            return text
        base = repo_rel.rstrip("/")
        for name in ("INDEX.md", "README.md", "STATE.md",
                     "index.md"):
            text = repo.show(head, f"{base}/{name}")
            if text is not None:
                return text
    return None


def pointer_key(pointer):
    """A withheld pointer's identity, where one must persist
    (the state footer): a hash — the string itself never rides
    any output (C6; the sibling's pred_key precedent)."""
    return hashlib.sha1((pointer or "").encode()) \
        .hexdigest()[:12]


# ------------------------------------------------------------------
# staleness (Q3: event-relative, one rule for all IDs)
# ------------------------------------------------------------------

def project_last_event(repo_root, root):
    """The project root's newest record-event date
    (YYYY-MM-DD, local): the newest file mtime under the
    root. Under the disk posture this is the event evidence
    the records themselves offer (the allowlist repo's
    history carries no charter events). Bounded walk."""
    base = os.path.join(repo_root, root)
    newest = None
    seen = 0
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames
                       if d not in PRUNE_DIRS]
        if os.path.relpath(dirpath, base).count(os.sep) >= 3:
            dirnames[:] = []
        for fn in filenames:
            seen += 1
            if seen > 20000:
                break
            try:
                mt = os.path.getmtime(os.path.join(dirpath, fn))
            except OSError:
                continue
            if newest is None or mt > newest:
                newest = mt
        if seen > 20000:
            break
    if newest is None:
        return None
    return datetime.fromtimestamp(newest).strftime("%Y-%m-%d")


def row_stale(row, last_event_date):
    """-> True (stale) · False (fresh) · None (no refresh date
    on the row — a blank field, which reads unknown per C2)."""
    m = DATE_RE.search(row["refreshed_at"] or "")
    if not m:
        return None
    refreshed = m.group(0)
    if last_event_date and last_event_date > refreshed:
        return True
    return False


# ------------------------------------------------------------------
# evidence resolution — one resolver per item ID (PLAN SS6).
# Each reads ONLY its record of record and yields
# (outcome, citation, reason, pair):
#   outcome: resolved · unknown · refuted
#   citation: `<kind> @ <path> (status: <value>)` — the record
#             and its own status value, never a paraphrase
#   pair: for refuted, the refuting record's citation (the
#         failed-check pair form)
# The pointer gate runs BEFORE any resolver: a withheld row
# never reaches this section (C6).
# ------------------------------------------------------------------

class Ctx:
    def __init__(self, repo, head, tree, records, workspace_root):
        self.repo = repo
        self.head = head
        self.tree = tree
        self.records = records
        self.ws = workspace_root
        self.prefs = set()   # excluded prefixes, set by the view
        self._registry = None
        self._floors = None

    def status_of(self, text, cited_id=None):
        bc = load_sibling()
        return bc.status_field(text, cited_id)

    def cite(self, kind, path, value):
        return f"{kind} @ {path} (status: {value})"

    # the automation registry (Q10's widened floors criteria
    # live behind these records — the owning seats' checks
    # compiled by `mica auto`; read, never re-derived)
    def registry(self):
        if self._registry is None:
            self._registry = {}
            p = os.path.join(self.ws, "data", "automation",
                             "registry.json")
            try:
                data = json.load(open(p))
                for e in data.get("entries", []):
                    if isinstance(e, dict) and e.get("id"):
                        self._registry[e["id"]] = e
            except (OSError, ValueError):
                pass
        return self._registry

    def floor_result(self, fid):
        p = os.path.join(self.ws, "data", "automation",
                         "floors", f"{fid}.json")
        try:
            return json.load(open(p))
        except (OSError, ValueError):
            return None


def _record_outcome(ctx, text, path, kind):
    """Shared shape for record-reading resolvers: resolved iff
    the record was read and carries a status field or content;
    a status value opening with a failure word is a refutation
    (the §9 pair), not a resolution."""
    if text is None:
        return ("unknown", None, "unresolvable", None)
    found, value, _closed = ctx.status_of(text)
    shown = value if found else "present"
    cite = ctx.cite(kind, path, shown)
    if found and re.match(r"(?i)(failed|refused|refuted|fail)\b",
                          value or ""):
        return ("refuted", cite, "record-refutes", cite)
    return ("resolved", cite, None, None)


def resolve_boundary(ctx, row, cand, charter):
    text = read_target(ctx.repo, ctx.head, cand)
    if text is None:
        return ("unknown", None, "unresolvable", None)
    if not re.search(r"^#{1,6}\s", text, re.M) \
            or not text.strip():
        return ("unknown", None, "insides-not-declared", None)
    return ("resolved",
            ctx.cite("boundary", cand[1] or cand[2], "present"),
            None, None)


def resolve_template_conformance(ctx, row, cand, charter):
    # a packet pointer resolves through the desks' homes (the
    # sibling Records.packets pattern); anything else is a
    # record read like the others
    bc = load_sibling()
    m = re.search(r"(\d{4})", row["evidence"])
    text = read_target(ctx.repo, ctx.head, cand)
    if text is not None:
        return _record_outcome(ctx, text, cand[1] or cand[2],
                               "conformance")
    if m:
        pk = ctx.records.packets()
        for desk, d in pk.items():
            if m.group(1) in d:
                closed, where = d[m.group(1)]
                state = "closed" if closed else "open"
                return ("resolved",
                        ctx.cite("packet", where, state),
                        None, None)
    return ("unknown", None, "unresolvable", None)


def resolve_visual_face(ctx, row, cand, charter):
    text = read_target(ctx.repo, ctx.head, cand)
    if text is None and not (cand[2] and os.path.isfile(cand[2])):
        return ("unknown", None, "unresolvable", None)
    return ("resolved",
            ctx.cite("visual", cand[1] or cand[2], "present"),
            None, None)


def resolve_business_gap(ctx, row, cand, charter):
    # the record of record is the designated charter's own
    # State line (self-pointer + anchor, the fold's precedent)
    text = charter.text
    m = re.search(r"Business gap, in one line:\s*(.*)", text)
    if not m:
        return ("unknown", None, "line-absent", None)
    value = m.group(1).strip().strip("*").strip()
    if not value or value.startswith("<"):
        # absent, or the template's angle-bracket placeholder
        # (which may wrap across lines) — not a named gap
        return ("unknown", None, "line-absent", None)
    return ("resolved",
            ctx.cite("charter-state", charter.path, "present"),
            None, None)


def resolve_floors(ctx, row, cand, charter):
    # Q10's widened criteria, as amended: the registry entry
    # resolves for the depended-on thing the pointer names +
    # floor asserts PASS (read from the registry's own records)
    ev = row["evidence"].split("#")[0].strip()
    reg = ctx.registry()
    fid = None
    if cand[0]:
        base = os.path.basename((cand[1] or cand[2] or "")
                                .rstrip("/"))
        fid = base[:-5] if base.endswith(".json") else base
        if fid in reg or ctx.floor_result(fid) is not None:
            pass
        elif ev in reg:
            fid = ev
        else:
            fid = None
    elif ev in reg:
        fid = ev
    if fid is None:
        return ("unknown", None, "registry-entry-unresolved",
                None)
    cite_path = f"data/automation/registry.json#{fid}"
    fr = ctx.floor_result(fid)
    if fr is not None:
        st = str(fr.get("status", "")).lower()
        fcite = ctx.cite("floor-assert",
                         f"data/automation/floors/{fid}.json",
                         st or "?")
        if st == "failed":
            return ("refuted", fcite, "assert-failed", fcite)
        if st in ("ok", "restored"):
            return ("resolved", fcite, None, None)
        return ("unknown", fcite, "assert-state-unread", None)
    entry = reg.get(fid)
    if entry is not None:
        st = "enabled" if entry.get("enabled") else "disabled"
        return ("resolved", ctx.cite("registry", cite_path, st),
                None, None)
    return ("unknown", None, "registry-entry-unresolved", None)


def resolve_tests(ctx, row, cand, charter):
    text = read_target(ctx.repo, ctx.head, cand)
    if text is None:
        return ("unknown", None, "unresolvable", None)
    green = re.search(
        r"(?im)^.*\b(ALL PASS|all pass|tests pass|PASS\s*\(|"
        r"green)\b.*$", text)
    broken = re.search(
        r"(?i)break[- ]evidence|deliberately broken|shown "
        r"fail|fails? on (a |the )?broken", text)
    cite = ctx.cite("test-record", cand[1] or cand[2], "present")
    if green and broken:
        return ("resolved", cite, None, None)
    if not broken:
        return ("unknown", cite, "no-break-evidence", None)
    return ("unknown", cite, "no-green-run", None)


def resolve_ladder(ctx, row, cand, charter):
    text = read_target(ctx.repo, ctx.head, cand)
    return _record_outcome(ctx, text, cand[1] or cand[2],
                           "gate-record")


def resolve_production_bar(ctx, row, cand, charter):
    # Judge-lane records only (PLAN SS6): a pointer resolving
    # anywhere else cannot resolve this row — this leg never
    # grades an axis
    rel = cand[1] or ""
    disk = cand[2] or ""
    judge_disk = os.path.join(ctx.ws, "flows", "judge")
    if not (rel.startswith(JUDGE_HOME + "/")
            or disk.startswith(judge_disk)):
        return ("unknown", None, "not-a-judge-record", None)
    text = read_target(ctx.repo, ctx.head, cand)
    return _record_outcome(ctx, text, cand[1] or cand[2],
                           "judge-record")


def resolve_provenance(ctx, row, cand, charter):
    text = read_target(ctx.repo, ctx.head, cand)
    if text is None:
        return ("unknown", None, "unresolvable", None)
    if not DATE_RE.search(text):
        return ("unknown", None, "log-shape-unread", None)
    return ("resolved",
            ctx.cite("log", cand[1] or cand[2], "present"),
            None, None)


def resolve_privacy(ctx, row, cand, charter):
    # the charter's own gates (+ the flip record where the
    # pointer names one): a self-pointer reads the charter's
    # gate language; another record reads its status field
    if cand[1] == charter.path:
        if re.search(r"(?i)public flip|private stays private|"
                     r"no public|Curtis.{0,30}\btap\b",
                     charter.text):
            return ("resolved",
                    ctx.cite("charter-gates", charter.path,
                             "present"), None, None)
        return ("unknown", None, "gates-unread", None)
    text = read_target(ctx.repo, ctx.head, cand)
    return _record_outcome(ctx, text, cand[1] or cand[2],
                           "flip-record")


RESOLVERS = {
    "boundary-current": resolve_boundary,
    "template-conformance": resolve_template_conformance,
    "visual-face": resolve_visual_face,
    "business-gap-line": resolve_business_gap,
    "floors-registered": resolve_floors,
    "tests-break-evidence": resolve_tests,
    "ladder-rungs": resolve_ladder,
    "production-bar-axes": resolve_production_bar,
    "provenance-current": resolve_provenance,
    "privacy-law-held": resolve_privacy,
}


# ------------------------------------------------------------------
# checker records (Q5): the citation binding is a STATE-line
# `needs: <item-id> = <state>` in a checker record bound to the
# project by HOME or by CHARTER CITATION. Prose mentions mint
# nothing. Sources at v1: desk packets' STATE.md (the desks'
# homes, live) + records under each project root on disk
# (cycle.md · STATE.md · *gate*.md — present-state).
# ------------------------------------------------------------------

GRADER_HOMES = ("workspace/flows/judge/",
                "workspace/flows/meta-forge/",
                "workspace/flows/template-steward/")
PACKET_STATES = ("completed", "ledger", "in-progress", "backlog",
                 "inbox", "routed", "modelling")


def _needs_lines(text):
    out = []
    for m in NEEDS_LINE.finditer(text or ""):
        rid, state = m.group(1), m.group(2).lower()
        if rid in TEN_IDS and (state in STATE_RANK
                               or state == "failed"):
            out.append((rid, state))
    return out


def _cited_projects(text, designated):
    """Projects a record binds to by charter citation: a path
    token in the record naming a designated charter (any of
    its spellings)."""
    bc = load_sibling()
    hits = set()
    for cite in bc.extract_citations(text or ""):
        if cite["kind"] != "path":
            continue
        p = cite["path"].rstrip(".,;:")
        forms = {p, p.lstrip("~/")}
        if p.startswith("flows/") or p.startswith("projects/"):
            forms.add("workspace/" + p)
        for path, root in designated.items():
            if path in forms:
                hits.add(root)
    return hits


def collect_checker_records(repo, head, tree, records,
                            projects, workspace_root):
    """-> {root: {item: [ {state, cite, grader, home} ]}} —
    every STATE-line binding found, with its citation in the
    SS7.2 form. `home` marks a packet's board state (for the
    claimed rule) or the record's repo-relative home."""
    designated = {}
    for root, pr in projects.items():
        for c in pr["designated"]:
            designated[c.path] = root
    bindings = {}

    def add(root, rid, state, cite, grader, home):
        bindings.setdefault(root, {}).setdefault(rid, []) \
            .append({"state": state, "cite": cite,
                     "grader": grader, "home": home})

    # desk packets: STATE.md under each desk/state/packet dir
    for desk_root in records.desk_roots:
        if not os.path.isdir(desk_root):
            continue
        for desk in sorted(os.listdir(desk_root)):
            ddir = os.path.join(desk_root, desk)
            if not os.path.isdir(ddir):
                continue
            for pstate in PACKET_STATES:
                sdir = os.path.join(ddir, pstate)
                if not os.path.isdir(sdir):
                    continue
                for name in sorted(os.listdir(sdir)):
                    spath = os.path.join(sdir, name, "STATE.md")
                    if not os.path.isfile(spath):
                        continue
                    try:
                        text = open(spath, errors="replace").read()
                    except OSError:
                        continue
                    lines = _needs_lines(text)
                    if not lines:
                        continue
                    roots = _cited_projects(text, designated)
                    where = f"{desk}/{pstate}/{name}"
                    grader = pstate in ("completed", "ledger")
                    for rid, state in lines:
                        cite = records_cite("packet", where,
                                            state)
                        for root in roots:
                            add(root, rid, state, cite, grader,
                                pstate)
    # project-home records: cycle.md · STATE.md · *gate*.md
    for root in projects:
        base = os.path.join(workspace_root,
                            root[len("workspace/"):]
                            if root.startswith("workspace/")
                            else root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            depth = os.path.relpath(dirpath, base).count(os.sep)
            if depth > 2:
                dirnames[:] = []
                continue
            for fn in filenames:
                low = fn.lower()
                if low not in ("cycle.md", "state.md") \
                        and "gate" not in low:
                    continue
                fpath = os.path.join(dirpath, fn)
                try:
                    text = open(fpath, errors="replace").read()
                except OSError:
                    continue
                lines = _needs_lines(text)
                if not lines:
                    continue
                rel = os.path.relpath(fpath, repo.root)
                grader = any(rel.startswith(g)
                             for g in GRADER_HOMES)
                cited = _cited_projects(text, designated)
                roots = {root} | cited
                for rid, state in lines:
                    cite = records_cite("record", rel, state)
                    for r2 in roots:
                        if r2 in projects:
                            add(r2, rid, state, cite, grader,
                                "home")
    return bindings


def records_cite(kind, where, state):
    return f"{kind} @ {where} (needs-state: {state})"


# ------------------------------------------------------------------
# the projection: parse -> gate -> resolve -> staleness ->
# work state (PLAN SS7). The charter's declaration is never a
# state (C1); a state exists only with its checker citation.
# ------------------------------------------------------------------

def build_needs_view(repo, head, records, workspace_root):
    bc = load_sibling()
    tree = repo.ls_tree(head)
    paths = enumerate_charter_paths(workspace_root, repo.root)
    record_files = list(paths)
    for p in paths:
        lm = os.path.join(os.path.dirname(p), "LANE_MEMORY.md")
        record_files.append(lm)
    prefs, all_lanes = excluded_prefixes(
        repo, head, tree, workspace_root, record_files)
    projects, _charters = census(repo, tree, prefs,
                                 workspace_root, paths)
    ctx = Ctx(repo, head, tree, records, workspace_root)
    ctx.prefs = prefs
    bindings = collect_checker_records(repo, head, tree,
                                       records, projects,
                                       workspace_root)
    view = {"head": head, "projects": [], "findings": [],
            "pairs": [], "unestablished_grade": 0,
            "coverage": {}, "snapshot": {}}
    cov = {"projects_total": 0, "projects_indexed": 0,
           "rows": 0, "resolved": 0, "unknown": 0, "withheld": 0,
           "refuted": 0}
    state_counts = {s: 0 for s in WORK_STATES}
    for root in sorted(projects):
        pr = projects[root]
        seat = owning_seat(root, all_lanes)
        pv = {"root": root, "seat": seat, "rows": [],
              "findings": [], "kind": None, "charter": None}
        cov["projects_total"] += 1
        if len(pr["designated"]) > 1:
            pv["kind"] = "double"
            paths = sorted(c.path for c in pr["designated"])
            pv["designated_paths"] = paths
            view["findings"].append({
                "kind": "double-designation", "project": root,
                "paths": paths, "seat": seat})
            view["projects"].append(pv)
            continue
        if not pr["designated"]:
            pv["kind"] = "unindexed"
            pv["note"] = ("no designated charter"
                          if not pr["attributed"] else
                          "charters point elsewhere; no "
                          "designated index of its own")
            view["projects"].append(pv)
            continue
        charter = pr["designated"][0]
        pv["charter"] = charter
        rows, parse_findings, has_block = parse_index_block(
            charter.text)
        if not has_block:
            pv["kind"] = "unindexed"
            pv["note"] = "designated charter carries no " \
                         "needs-index block"
            view["projects"].append(pv)
            continue
        pv["kind"] = "indexed"
        cov["projects_indexed"] += 1
        for f in parse_findings:
            pv["findings"].append(f)
            view["findings"].append({
                "kind": "parse", "project": root, "detail": f})
        last_event = project_last_event(repo.root, root)
        for rid in TEN_IDS:
            rv = project_row(ctx, root, rid, rows.get(rid),
                             charter, last_event,
                             bindings.get(root, {}).get(rid, []),
                             view)
            pv["rows"].append(rv)
            cov["rows"] += 1
            if rv["outcome"] == "pointer-withheld":
                cov["withheld"] += 1
            elif rv["outcome"] in cov:
                cov[rv["outcome"]] += 1
            if rv["state"] in state_counts:
                state_counts[rv["state"]] += 1
            snap = {"s": rv["state"], "o": rv["outcome"],
                    "f": 1 if rv["pair"] else 0,
                    "h": rv["identity"]}
            view["snapshot"][f"{root}|{rid}"] = snap
        view["projects"].append(pv)
    cov["states"] = state_counts
    view["coverage"] = cov
    prev_text = repo.show(head, NEEDS_PATH)
    view["prev_stamp"] = bc.board_stamp(prev_text)
    view["prev_snapshot"] = needs_snapshot(prev_text)
    view["prev_text"] = prev_text
    return view


def needs_snapshot(board_text):
    if not board_text:
        return {}
    m = re.search(r"<!-- needs-state: (\{.*?\}) -->",
                  board_text, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(1)).get("rows", {})
    except json.JSONDecodeError:
        return {}


def project_row(ctx, root, rid, row, charter, last_event,
                binds, view):
    meta = ITEM_META[rid]
    rv = {"id": rid, "checker": meta["checker"],
          "pool": meta["pool"], "section": meta["section"],
          "applies": None, "evidence_shown": "—",
          "refreshed_at": "—", "outcome": "unknown",
          "reason": None, "state": None, "cite": None,
          "checker_cite": None, "pair": None, "identity": rid}
    if row is None:
        rv["reason"] = "missing-row"
        return rv
    rv["applies"] = row["applies"]
    rv["refreshed_at"] = row["refreshed_at"]
    ev = row["evidence"]
    stale = row_stale(row, last_event)
    if row["applies"] not in ("yes", "no", "unassessed"):
        rv["reason"] = "bad-applies"
        rv["evidence_shown"] = ev
        return rv
    if row["applies"] == "unassessed":
        rv["reason"] = "unassessed"
        rv["evidence_shown"] = ev
        return rv
    cand = None
    if ev != "—":
        cand = normalize_pointer(ev, charter.path, ctx.tree,
                                 ctx.repo.root)
        if cand[1] and path_excluded(cand[1], ctx.prefs):
            rv["outcome"] = "pointer-withheld"
            rv["evidence_shown"] = "(pointer withheld)"
            rv["identity"] = pointer_key(ev)
            return rv
    if row["applies"] == "no":
        # Q6: out of the five states entirely; counts as
        # resolved in coverage when its basis resolves
        rv["state"] = "not-applicable"
        if ev == "—":
            rv["reason"] = "no-without-basis"
            return rv
        rv["evidence_shown"] = ev
        if cand is None or not cand[0]:
            rv["reason"] = "unresolvable"
            return rv
        text = read_target(ctx.repo, ctx.head, cand)
        if text is None:
            rv["reason"] = "unresolvable"
            return rv
        if stale is None:
            rv["reason"] = "no-refresh-date"
            return rv
        if stale:
            rv["reason"] = "stale"
            return rv
        rv["outcome"] = "resolved"
        rv["cite"] = ctx.cite("basis", cand[1] or cand[2],
                              "present")
        return rv
    # applies: yes
    if ev == "—":
        rv["reason"] = "no-pointer"
        return rv
    rv["evidence_shown"] = ev
    if (cand is None or not cand[0]) \
            and rid != "floors-registered":
        rv["reason"] = "unresolvable"
        return rv
    # floors-registered's pointer may be a bare registry
    # identifier rather than a path (C4) — its resolver decides
    outcome, cite, reason, pair = RESOLVERS[rid](ctx, row, cand,
                                                 charter)
    rv["cite"] = cite
    rv["reason"] = reason
    if outcome == "resolved" and stale is None:
        outcome, rv["reason"] = "unknown", "no-refresh-date"
        rv["cite"] = cite
    elif outcome == "resolved" and stale:
        outcome, rv["reason"] = "unknown", "stale"
    rv["outcome"] = outcome
    if pair:
        rv["pair"] = pair
    # work state from checker bindings (Q5's citation binding)
    minted = {}
    for b in binds:
        st = b["state"]
        if st == "failed":
            continue
        if st == "claimed":
            if b["home"] == "in-progress":
                minted.setdefault("claimed", b)
        elif st == "graded":
            if b["grader"]:
                minted.setdefault("graded", b)
            else:
                view["unestablished_grade"] += 1
        else:
            minted.setdefault(st, b)
    failed = [b for b in binds if b["state"] == "failed"]
    state, establisher = "pending", None
    for st in ("graded", "verified", "checked", "claimed"):
        if st in minted:
            state, establisher = st, minted[st]
            break
    pair_listed = False
    if failed:
        rv["pair"] = rv["pair"] or failed[0]["cite"]
        view["pairs"].append({
            "project": root, "item": rid,
            "record": failed[0]["cite"],
            "conflict": state in ("checked", "verified",
                                  "graded")})
        pair_listed = True
        state, establisher = "pending", None
    if rv["outcome"] == "refuted":
        if not pair_listed:
            view["pairs"].append({
                "project": root, "item": rid,
                "record": rv["pair"] or rv["cite"],
                "conflict": False})
        state, establisher = "pending", None
    rv["state"] = state
    if establisher:
        rv["checker_cite"] = establisher["cite"]
    rv["identity"] = hashlib.sha1(
        f"{rv['cite'] or ''}|{rv['checker_cite'] or ''}".encode()
    ).hexdigest()[:12] if (rv["cite"] or rv["checker_cite"]) \
        else rid
    return rv


# ------------------------------------------------------------------
# rendering (PLAN SS7.3): coverage on the face · one section per
# project · per-desk pending renders cut by checker field ·
# the machine footer carrying the state snapshot.
# ------------------------------------------------------------------

def strip_compiled_at(text):
    """The volatile header lines for change comparison: the
    compiled-at clock and the compiled-through stamp (the
    stamp advances to HEAD whenever any board commit lands,
    including this compiler's own — it is not a content
    change)."""
    if not text:
        return ""
    text = re.sub(r"^compiled-at: .*$", "compiled-at:", text,
                  flags=re.M)
    text = re.sub(r"^compiled-through: .*$", "compiled-through:",
                  text, flags=re.M)
    # the per-project read citation carries the same stamp
    return re.sub(r"(index of record: \S+) @ [0-9a-f]{12}",
                  r"\1 @", text)


def render_needs(view, stamp, compiled_at):
    cov = view["coverage"]
    st = cov["states"]
    lines = []
    lines.append("# Project needs board — compiled from the "
                 "designated charters + checker records")
    lines.append("")
    lines.append(
        "_What this board proves: each project's declared needs "
        "index (its one designated charter) resolved against "
        "the record of record each row points to, and the work "
        "states checker records establish under the STATE-line "
        "citation binding. The charter declares; other records "
        "prove. A row's state exists only with the checker "
        "citation that establishes it; a missing row, blank "
        "field, unresolvable pointer, or stale refresh reads "
        "unknown — never satisfied, never failed. Pointers into "
        "excluded homes render pointer-withheld and carry "
        "nothing. This board never grades._")
    lines.append("")
    lines.append(
        f"coverage: indexed {cov['projects_indexed']}/"
        f"{cov['projects_total']} projects · rows resolved "
        f"{cov['resolved']} · unknown {cov['unknown']} · "
        f"pointer-withheld {cov['withheld']} · refuted "
        f"{cov['refuted']} (of {cov['rows']} declared rows) · "
        f"states pending {st['pending']} · claimed "
        f"{st['claimed']} · checked {st['checked']} · verified "
        f"{st['verified']} · graded {st['graded']}")
    lines.append(f"compiled-through: {stamp}")
    lines.append(f"compiled-at: {compiled_at}")
    lines.append(
        "known limit (v1): grouping is by project root — two "
        "designated charters in DIFFERENT roots read as two "
        "projects (cross-root duplicates need a project key "
        "the fold has not named).")
    lines.append("")
    pending_by_section = {}
    for pv in view["projects"]:
        root = pv["root"]
        seat = f" — owning seat: {pv['seat']}" if pv["seat"] \
            else ""
        if pv["kind"] == "double":
            lines.append(f"## {root}{seat}")
            lines.append(
                "- ⚠ FINDING double-designation: more than one "
                "designated project-needs index under this "
                "project root — " +
                " · ".join(pv["designated_paths"]) +
                " — a finding to the owning seat; no row from "
                "any of them is parsed (C3, never a silent merge)")
            lines.append("")
            continue
        if pv["kind"] == "unindexed":
            lines.append(f"## {root}{seat}")
            lines.append(f"- state: unindexed — {pv['note']} — "
                         f"a state line, not an empty board")
            lines.append("")
            continue
        ch = pv["charter"]
        lines.append(f"## {root}{seat}")
        lines.append(f"- index of record: {ch.path} @ "
                     f"{view['head'][:12]}")
        for rv in pv["rows"]:
            if rv["applies"] is None:
                lines.append(f"- {rv['id']} · row missing from "
                             f"the index — unknown (missing-row)")
                continue
            seg = [f"- {rv['id']} · applies: {rv['applies']}",
                   f"evidence: {rv['evidence_shown']}",
                   f"refreshed_at: {rv['refreshed_at']}",
                   f"→ {rv['outcome']}"]
            if rv["reason"] and rv["outcome"] == "unknown":
                seg.append(f"({rv['reason']})")
            if rv["state"] and rv["state"] != "not-applicable":
                seg.append(f"· state: {rv['state']}")
            elif rv["state"] == "not-applicable":
                seg.append("· not applicable (basis cited)")
            if rv["cite"]:
                seg.append(f"· record: {rv['cite']}")
            if rv["checker_cite"]:
                seg.append(f"· checker: {rv['checker_cite']}")
            if rv["pair"]:
                seg.append(f"· ⚠ pair: {rv['id']} ↔ "
                           f"{rv['pair']}")
            lines.append(" ".join(seg))
            if rv["state"] == "pending":
                pending_by_section.setdefault(
                    rv["section"], []).append(
                    f"{root} · {rv['id']} ({rv['outcome']})")
        for f in pv["findings"]:
            lines.append(f"- ⚠ {f}")
        lines.append("")
    if pending_by_section:
        lines.append("## Pending by checker (renders of this "
                     "compilation, cut by checker field)")
        lines.append("")
        for section in SECTION_ORDER:
            rows = pending_by_section.get(section)
            if not rows:
                continue
            lines.append(f"### {section}")
            for r in rows:
                lines.append(f"- {r}")
            lines.append("")
    snap = json.dumps({"rows": view["snapshot"]},
                      sort_keys=True)
    lines.append(f"<!-- needs-state: {snap} -->")
    lines.append("")
    return "\n".join(lines)


def needs_ledger_events(view):
    """State transitions + pair appearances, by comparison
    against the previous board's footer snapshot — content-
    keyed, so a recorded change can never re-fire (SS8.3)."""
    prev = view["prev_snapshot"]
    events = []
    for key, cur in sorted(view["snapshot"].items()):
        old = prev.get(key)
        if old == cur:
            continue
        root, rid = key.rsplit("|", 1)
        if old is None or old.get("s") != cur["s"] \
                or old.get("f") != cur["f"]:
            events.append({
                "kind": "state", "ts": now_iso(),
                "project": root, "item": rid,
                "from": old.get("s") if old else None,
                "to": cur["s"], "pair": bool(cur["f"])})
    return events


# ------------------------------------------------------------------
# the scan guard (packets 0018/0019, shared): the sweep's
# patterns over the needs pair too — the sibling's
# scan_composed covers its own pair with its own path labels.
# ------------------------------------------------------------------

def scan_texts(pairs):
    bc = load_sibling()
    hits = []
    for path, text in pairs:
        for name, pat in bc.load_sweep_patterns():
            if pat.search(text):
                hits.append((path, name))
    return hits


# ------------------------------------------------------------------
# modes
# ------------------------------------------------------------------

def compose_sibling(repo, records, head0):
    """The rolling board's half of the joint pass, composed
    from board-compiler's own primitives exactly as its
    do_write composes them (walk -> dependency flips ->
    compose -> render -> ledger) — the code is imported, not
    copied; the write itself is the joint one below."""
    bc = load_sibling()
    v = bc.build_view(repo, head0, records)
    stamp = v.prev_stamp
    rebaselined = stamp is not None \
        and not repo.is_ancestor(stamp, head0)
    baseline = stamp is None or rebaselined
    raw_events, commits = [], []
    if not baseline:
        raw_events, commits = bc.walk_flips(
            repo, stamp, head0, v.included, v.tree)
    new_snapshot = {}
    for slug, entry in v.entries.items():
        if entry["band"] and entry["note"] in ("ok", "followed"):
            flips, snap = bc.dependency_flips(
                records, entry["lane"], entry["band"],
                v.prev_snapshot, None)
            raw_events.extend(flips)
            new_snapshot.update(snap)
    composed = bc.compose_events(v, raw_events, head0)
    bc.finish_view_counts(v, composed)
    touched = bc.sweep_touched_lanes(commits, v.included) \
        if commits else "none (baseline)" if baseline else "none"
    rendered = bc.render_board(v, head0, new_snapshot, touched,
                               bc.now_iso())
    ledger_old = repo.show(head0, bc.LEDGER_PATH) or ""
    lines = [ln for ln in ledger_old.splitlines() if ln.strip()]
    if not lines:
        lines.append(json.dumps({"kind": "genesis",
                                 "ts": bc.now_iso(),
                                 "stamp": head0}))
    lines += [json.dumps(e, ensure_ascii=False) for e in composed]
    ledger_new = "\n".join(lines) + "\n"
    changed = baseline or bool(commits) or bool(composed)
    info = {"baseline": baseline, "rebaselined": rebaselined,
            "commits_walked": len(commits),
            "events": len(composed),
            "pairs": sum(len(e["pairs"])
                         for e in v.entries.values()),
            "coverage": f"{v.resolved_lines}/{v.total_lines}"}
    return rendered, ledger_new, changed, info


def do_write(repo, records, workspace_root):
    import fcntl
    bc = load_sibling()
    gitdir = repo.git("rev-parse",
                      "--absolute-git-dir").stdout.strip()
    lockf = open(os.path.join(gitdir, "board-compiler.lock"),
                 "a+")
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        msg = "writer lock held — pass deferred whole to the " \
              "next tick"
        if JSON_MODE:
            print(json.dumps({"deferred": True, "reason": msg}))
        else:
            print(f"needs-compiler: {msg}")
        return 0
    bc.set_alert_path(workspace_root)
    head0 = repo.head()
    # ---- compose BOTH boards under the one lock (Q4)
    sib_rendered, sib_ledger, sib_changed, sib_info = \
        compose_sibling(repo, records, head0)
    view = build_needs_view(repo, head0, records,
                            workspace_root)
    events = needs_ledger_events(view)
    needs_rendered = render_needs(view, head0, now_iso())
    needs_old = repo.show(head0, NEEDS_LEDGER_PATH) or ""
    nlines = [ln for ln in needs_old.splitlines() if ln.strip()]
    if not nlines:
        nlines.append(json.dumps({"kind": "genesis",
                                  "ts": now_iso(),
                                  "stamp": head0}))
    nlines += [json.dumps(e, ensure_ascii=False) for e in events]
    needs_ledger = "\n".join(nlines) + "\n"
    prev_needs = view["prev_text"]
    needs_changed = prev_needs is None or bool(events) or \
        strip_compiled_at(needs_rendered) != \
        strip_compiled_at(prev_needs)
    # no-op discipline: neither board changed -> commit nothing
    if not sib_changed and not needs_changed:
        if JSON_MODE:
            print(json.dumps({"noop": True, "head": head0}))
        else:
            print(f"needs: no changes on either board — "
                  f"nothing committed (head {head0[:12]})")
        return 0
    # ---- the scan guard over all four composed files
    hits = bc.scan_composed(sib_rendered, sib_ledger)
    hits += scan_texts([(NEEDS_PATH, needs_rendered),
                        (NEEDS_LEDGER_PATH, needs_ledger)])
    if hits:
        bc.write_refusal_alert(flagged=[{"file": p,
                                         "pattern": n}
                                        for p, n in hits])
        detail = "; ".join(f"{p} matches sweep pattern class {n}"
                           for p, n in hits)
        fail(f"secret-scan refusal: {detail} — commit refused, "
             f"stamps unmoved (the interval re-compiles next "
             f"tick)")
    # ---- compose -> temp -> rename -> ONE commit (both pairs)
    tmpdir = os.path.join(gitdir, "board-compiler-tmp")
    os.makedirs(tmpdir, exist_ok=True)
    board_dir = os.path.join(repo.root, "memory", "board")
    os.makedirs(board_dir, exist_ok=True)
    files = {bc.BOARD_PATH: sib_rendered,
             bc.LEDGER_PATH: sib_ledger,
             NEEDS_PATH: needs_rendered,
             NEEDS_LEDGER_PATH: needs_ledger}
    for rel, text in files.items():
        tmp = os.path.join(tmpdir, os.path.basename(rel))
        with open(tmp, "w") as fh:
            fh.write(text)
        os.replace(tmp, os.path.join(board_dir,
                                     os.path.basename(rel)))
    env = {"GIT_AUTHOR_NAME": bc.COMPILER_AUTHOR_NAME,
           "GIT_AUTHOR_EMAIL": bc.COMPILER_AUTHOR_EMAIL,
           "GIT_COMMITTER_NAME": bc.COMPILER_AUTHOR_NAME,
           "GIT_COMMITTER_EMAIL": bc.COMPILER_AUTHOR_EMAIL}
    paths = list(files)
    landed_by_sweep = False
    commit_sha = None
    for attempt in range(2):
        repo.git("add", "--", *paths, check=False)
        staged = repo.git("diff", "--cached", "--quiet", "--",
                          *paths, check=False)
        if staged.returncode == 0:
            if all(repo.show(repo.head(), p) == files[p]
                   for p in paths):
                landed_by_sweep = True
                break
            fail("nothing staged and HEAD's board files differ "
                 "from the rendered ones — refusing to claim "
                 "the write")
        r = repo.git("commit", "-q", "-m",
                     f"{bc.COMPILER_SUBJECT_PREFIX} compile "
                     f"through {head0[:12]}",
                     "-m", f"Compiled-Through: {head0}",
                     check=False, env_extra=env)
        if r.returncode == 0:
            commit_sha = repo.head()
            break
        if attempt == 0:
            import time
            time.sleep(2)
            continue
        fail(f"commit failed: {r.stderr.strip()[:240]}")
    # verified write: BOTH boards' stamps re-read at HEAD
    rb_board = bc.board_stamp(repo.show(repo.head(),
                                        bc.BOARD_PATH))
    rb_needs = bc.board_stamp(repo.show(repo.head(), NEEDS_PATH))
    if rb_board != head0 or rb_needs != head0:
        fail(f"read-back mismatch: HEAD stamps board="
             f"{rb_board} needs={rb_needs}, expected {head0}")
    bc.clear_refusal_alert()
    cov = view["coverage"]
    result = {"head": head0, "commit": commit_sha,
              "landed_by_sweep": landed_by_sweep,
              "sibling": sib_info,
              "needs": {"indexed": cov["projects_indexed"],
                        "projects": cov["projects_total"],
                        "resolved": cov["resolved"],
                        "unknown": cov["unknown"],
                        "withheld": cov["withheld"],
                        "refuted": cov["refuted"],
                        "events": len(events),
                        "findings": len(view["findings"])},
              "scan": {"classes": len(bc.load_sweep_patterns()),
                       "hits": 0},
              "verified_stamp": head0}
    if JSON_MODE:
        print(json.dumps(result))
    else:
        print(f"needs: one writer pass through {head0[:12]} — "
              f"both boards composed under the one lock")
        print(f"sibling board: coverage {sib_info['coverage']} "
              f"· events {sib_info['events']} · C7 pairs "
              f"{sib_info['pairs']}")
        print(f"needs board: indexed {cov['projects_indexed']}/"
              f"{cov['projects_total']} projects · rows "
              f"resolved {cov['resolved']} · unknown "
              f"{cov['unknown']} · withheld {cov['withheld']} "
              f"· refuted {cov['refuted']} · state events "
              f"{len(events)} · findings "
              f"{len(view['findings'])}")
        if landed_by_sweep:
            print("commit: landed by the sweep's commit — HEAD "
                  "copies verified identical")
        else:
            print(f"commit: {commit_sha[:12] if commit_sha else '—'}"
                  f" (board paths only; never pushed)")
        print(f"read-back: HEAD stamps board + needs = "
              f"{head0[:12]} ✓")
    return 0


def do_render(repo, records, workspace_root, out_path):
    head0 = repo.head()
    view = build_needs_view(repo, head0, records,
                            workspace_root)
    text = render_needs(view, head0, now_iso())
    if JSON_MODE:
        print(json.dumps({"head": head0,
                          "coverage": view["coverage"],
                          "findings": view["findings"],
                          "board": text}))
    elif out_path:
        with open(out_path, "w") as fh:
            fh.write(text)
        print(f"needs: rendered at {head0[:12]} → {out_path} "
              f"(read-only; nothing committed)",
              file=sys.stderr)
    else:
        print(text)
    return 0


def do_check(repo, records, workspace_root, more=False):
    head0 = repo.head()
    view = build_needs_view(repo, head0, records,
                            workspace_root)
    cov = view["coverage"]
    findings = list(view["findings"])
    for p in view["pairs"]:
        findings.append({"kind": "pair", "project": p["project"],
                         "item": p["item"],
                         "record": p["record"],
                         "conflict": p["conflict"]})
    if JSON_MODE:
        print(json.dumps({"head": head0, "coverage": cov,
                          "findings": findings,
                          "pairs": view["pairs"],
                          "unestablished_grade":
                              view["unestablished_grade"]}))
    else:
        print(f"check @ {head0[:12]}: "
              f"{cov['projects_total']} projects "
              f"({cov['projects_indexed']} indexed) · "
              f"{len(findings)} finding(s) · "
              f"{cov['unknown']} unknown row(s) (never "
              f"findings) · {cov['withheld']} withheld · "
              f"{view['unestablished_grade']} unestablished "
              f"grade line(s) (noted, not minted)")
        ordered = [f for f in findings if f["kind"] == "pair"] \
            + [f for f in findings if f["kind"] != "pair"]
        show = ordered if more else ordered[:10]
        for f in show:
            if f["kind"] == "double-designation":
                print(f"- ⚠ double-designation in {f['project']}"
                      f": {' · '.join(f['paths'])} — finding "
                      f"to the owning seat")
            elif f["kind"] == "parse":
                print(f"- ⚠ {f['project']}: {f['detail']}")
            elif f["kind"] == "pair":
                print(f"- ⚠ pair: {f['project']} · {f['item']} "
                      f"↔ {f['record']}"
                      + (" (a checker state stands refuted)"
                         if f["conflict"] else ""))
    return 1 if findings else 0


def main(argv):
    global JSON_MODE
    bc = load_sibling()
    args = argv[1:]
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0
    mode = "render"
    repo_root, ws_root, desks_arg = HOME, None, None
    out_path, more = None, False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--write":
            mode = "write"
        elif a == "--render":
            mode = "render"
        elif a == "--check":
            mode = "check"
        elif a == "--json":
            JSON_MODE = True
        elif a == "--more":
            more = True
        elif a == "--repo":
            i += 1
            repo_root = args[i]
        elif a == "--workspace-root":
            i += 1
            ws_root = args[i]
        elif a == "--desks-root":
            i += 1
            desks_arg = args[i]
        elif a == "--out":
            i += 1
            out_path = args[i]
        else:
            print(__doc__, file=sys.stderr)
            return 2
        i += 1
    repo = bc.Repo(os.path.expanduser(repo_root))
    if not os.path.isdir(os.path.join(repo.root, ".git")) and \
            repo.git("rev-parse", "--git-dir",
                     check=False).returncode:
        fail(f"{repo_root} is not a git repository")
    ws = ws_root or os.path.join(repo.root, "workspace")
    desk_roots = [desks_arg] if desks_arg else \
        [os.path.join(HOME, "skills"), "/opt/muse/skills"]
    records = bc.Records(ws, desk_roots, home=repo.root)
    if mode == "write":
        return do_write(repo, records, ws)
    if mode == "check":
        return do_check(repo, records, ws, more)
    return do_render(repo, records, ws, out_path)


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    sys.exit(main(sys.argv))
