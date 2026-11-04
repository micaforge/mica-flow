#!/usr/bin/env python3
"""board-compiler — the rolling board compiler (dev-desk packet 0017,
Front Desk item 0002's build leg). One Python 3 file, stdlib only.

WHAT IT DOES
  Compiles each lane's middle-band queue state (LANE_MEMORY NEXT /
  JUST DID) from the memory git tree into a generated board that
  lives IN the memory repo (memory/board/BOARD.md), so diff-belief
  can read the board's own movement. It supersedes the mechanism of
  `mica lane board` (lb02): a snapshot glob over the live worktree
  becomes an interval compile over git objects, under a
  single-writer lock.

MODES
  --write    the single writer: compile the interval (the board's
             compiled-through stamp -> HEAD), replay flips in stem
             order, compose one ping per flip into the ping ledger,
             render the board, scan the composed board + ledger
             with the sweep's secret-scan patterns (packet 0018 —
             a hit refuses the commit, exit 1), and land board +
             ledger in ONE commit. Takes the writer flock; if the
             lock is held, the run defers whole to the next tick
             (exit 0, one line).
  --render   read-only: render the board at HEAD to stdout (or
             --out FILE). Never pings, never commits, takes no lock
             (it reads immutable HEAD objects — the lock arbitrates
             writer-vs-writer only).
  --check    the checker leg (read-only): C7 citation pairs + C2
             freshness prompts + unresolvable-assignment findings +
             schema states, per included lane. Exit 1 if any C7 pair
             (a would-mislead finding) exists, else 0.

OPTIONS
  --repo PATH        the home/memory repo (default ~). All lane +
                     inclusion reads are git objects at a named sha.
  --workspace-root   where cited records live on disk (cycles, taps);
                     default <repo>/workspace. Cited-record states
                     are read live, exactly as the C7 calibration
                     read them — the repo governs lanes + inclusion;
                     the records a queue cites are present-state.
  --desks-root       desk packages root for packet citations
                     (default ~/skills, /opt/muse/skills scanned).
  --out FILE         --render output file instead of stdout.
  --json             machine mode: one object, never truncated.
  --more             full listing where the brief truncates.
  --help             this surface; exits 0.

THE LAW IT RUNS UNDER (a06 DESIGN + Inés's six conditions, folded)
  - Compile the INTERVAL (cond. 6): walk stamp..HEAD, flips replayed
    in stem order; A->B->C in one interval wakes B's holder too.
    One ping per flip, keyed by flip identity in the ping ledger;
    intervals are disjoint by construction, so a recorded flip
    cannot re-fire. A ping unanswered is a board state (awaiting,
    age shown), never a repeat ping.
  - Inclusion-by-property is structural (conds. 3-5): checker,
    board, and pings EACH resolve inclusion from the lane's OWN
    seat-record marking (<!-- doorway-scope: excluded -->),
    INDEX-resolved, evaluated at HEAD (gate ruling Q-3), the read
    set built before any lane file opens. The property test is a
    `git grep -q` against the record path at HEAD: an excluded
    lane's bytes are never ingested by this tool. No lane name is
    named in this code.
  - The references rule (cond. 4) at extraction AND at the ping
    composer: a line pointing INTO an excluded home renders
    pointer-withheld; the board and the ledger never carry an
    excluded pointer.
  - Pointer stubs are followed under the same property rules, or
    rendered AS stubs — never as empty queues (cond. 2). A lane
    that cannot be parsed renders as a stub entry naming its state.
  - The board's claim is only what the checks prove (cond. 1): C7
    pairs + C2 anomalies-as-prompts, with the coverage line on its
    face. C7 resolution obeys R1-R6 (the 2026-11-04 calibration).
  - The board, its history, and the ping ledger never travel beyond
    the memory repo's read boundary (cond. 5). The compiler never
    pushes; the sweep's existing push carries its commits.
  - The scan guard (packet 0018): the compiler commits directly,
    outside the sweep's commit path, so --write carries the sweep's
    gate itself — the SWEEP'S OWN secret-scan patterns, imported
    live from ~/workspace/bin/memory-commit-sweep (never copied),
    run over the composed board + ledger inside the lock, ahead of
    the commit. A hit refuses the whole compile: no commit, the
    stamp unmoved, and no ping dispatch (pings exist only as
    committed ledger lines — the courier reads the ledger at HEAD),
    so the interval re-compiles whole on the next tick. The finding
    names file + pattern class, never the matched value. If the
    sweep's patterns cannot be loaded, the write fails rather than
    commit unscanned.
  - The refusal alert (packet 0019): a refusal only the cron's exit
    code carries is half a guard (0018 review, N3), so a refused
    --write also leaves the sweep-alert.json shape behind —
    <workspace>/data/lane/board-alert.json, {"ts", "flagged":
    [{"file", "pattern"}]} on a hit, {"ts", "error", "flagged"} on
    an unloadable pattern source, the value never persisted. The
    write sits after the refusal decision: its failure is a stderr
    note and the refusal stands. A successful compile unlinks it —
    the sweep's lifecycle (present only while something needs
    eyes). The reader is the board-refusal-watch hook, which wakes
    this lane's lead seat with the alert as payload.
  - Single-writer discipline vs the memory sweep: the compiler
    compiles against HEAD0 captured under its own flock, writes
    board + ledger to a temp path under .git/ and atomically
    renames them in immediately before its single commit, which
    touches only memory/board/**. If a sweep commit lands the
    renamed files first (whole-tree case), an empty commit is
    SUCCESS when HEAD's copies match the rendered ones (the stamp
    commit may carry the sweep's identity; exclusion layer 3 is
    path-set-based and holds either way). Ordering invariant:
    compose -> write temp -> rename -> commit.
  - The compiler's own commits are path-excluded from wake
    triggers in three layers: the board subtree is excluded from
    this tool's walk pathspec; compiler commits carry the reserved
    subject prefix `board:` and a fixed author identity; the
    replay skips any commit whose touched-path set is a subset of
    the board subtree.

EXIT CODES: 0 ok (incl. lock-deferred) · 1 failure · 2 usage.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

# Read law inherited from the doorway (spec SS5, judgement 1b): git
# reads are plumbing under GIT_OPTIONAL_LOCKS=0, exported by this
# tool itself before any child runs.
os.environ["GIT_OPTIONAL_LOCKS"] = "0"

HOME = os.path.expanduser("~")
BOARD_PATH = "memory/board/BOARD.md"
LEDGER_PATH = "memory/board/ping-ledger.jsonl"
BOARD_SUBTREE = "memory/board/"
COMPILER_AUTHOR_NAME = "board-compiler"
COMPILER_AUTHOR_EMAIL = "board-compiler@gravicity.ai"
COMPILER_SUBJECT_PREFIX = "board:"

PROP_RE = re.compile(r"doorway-scope:\s*excluded")
UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

JSON_MODE = False


def fail(msg, code=1):
    if JSON_MODE:
        print(json.dumps({"error": msg}))
    else:
        print(f"board-compiler: {msg}", file=sys.stderr)
    sys.exit(code)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def age_str(seconds):
    seconds = max(0, int(seconds))
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    return f"{seconds // 86400}d"


# ------------------------------------------------------------------
# git plumbing (objects only for reads; add/commit only in --write)
# ------------------------------------------------------------------

class Repo:
    def __init__(self, root):
        self.root = root

    def git(self, *args, check=True, env_extra=None):
        env = dict(os.environ)
        if env_extra:
            env.update(env_extra)
        r = subprocess.run(["git", "-C", self.root, *args],
                           capture_output=True, text=True, env=env)
        if check and r.returncode != 0:
            fail(f"git {' '.join(args[:2])} failed: "
                 f"{r.stderr.strip()[:240]}")
        return r

    def head(self):
        return self.git("rev-parse", "HEAD").stdout.strip()

    def show(self, sha, path):
        """File content at sha, or None if absent there."""
        r = self.git("show", f"{sha}:{path}", check=False)
        if r.returncode != 0:
            return None
        return r.stdout

    def ls_tree(self, sha):
        out = self.git("ls-tree", "-r", "--name-only", sha).stdout
        return set(out.splitlines())

    def prop_at(self, sha, path):
        """The inclusion property test: does the record at sha carry
        the exclusion marking? Answered by git grep -q against the
        record path only — the file's bytes never enter this tool."""
        r = self.git("grep", "-q", "-F", "-e", "doorway-scope: excluded",
                     sha, "--", path, check=False)
        return r.returncode == 0

    def is_ancestor(self, a, b):
        r = self.git("merge-base", "--is-ancestor", a, b, check=False)
        return r.returncode == 0

    def log_range(self, a, b, pathspecs):
        """Commits in a..b (oldest first) touching any pathspec, with
        the paths each touched. Returns [{sha, date, subject, paths}]."""
        args = ["log", "--reverse", "--name-only",
                "--format=COMMIT%x09%H%x09%cI%x09%s",
                f"{a}..{b}", "--", *pathspecs]
        out = self.git(*args).stdout
        commits, cur = [], None
        for line in out.splitlines():
            if line.startswith("COMMIT\t"):
                _, sha, date, subject = line.split("\t", 3)
                cur = {"sha": sha, "date": date, "subject": subject,
                       "paths": []}
                commits.append(cur)
            elif line.strip() and cur is not None:
                cur["paths"].append(line.strip())
        return commits

    def log_touching(self, path, limit=1):
        """Newest commits touching a path (any history), newest first:
        [{sha, date, subject}]."""
        out = self.git("log", f"-{limit}", "--format=%H%x09%cI%x09%s",
                       "--", path).stdout
        res = []
        for line in out.splitlines():
            if not line.strip():
                continue
            sha, date, subject = line.split("\t", 2)
            res.append({"sha": sha, "date": date, "subject": subject})
        return res


# ------------------------------------------------------------------
# lanes INDEX (parsed from the HEAD object) + inclusion resolution
# ------------------------------------------------------------------

class Lane:
    def __init__(self, slug):
        self.slug = slug
        self.flows = []          # flow-dir slugs, INDEX order
        self.chat_id = None
        self.lead = ""
        self.band_candidates = []  # repo-relative paths, priority order
        self.record_paths = []     # the lane's OWN records (property home)
        self.excluded = False
        self.stub_target = None    # set when the band is a pointer stub


def parse_index(text):
    """INDEX rows -> {slug: Lane}. Two shapes exist in the wild: the
    table (| slug | flows | chat | lead | state |) and arrow bullets
    (- **slug** -> `path`) for lanes registered by pointer."""
    lanes = {}
    if not text:
        return lanes
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 4:
                continue
            slug = cells[0]
            if not slug or slug in ("Lane", "------") or " " in slug \
                    or slug.startswith("---"):
                continue
            lane = lanes.setdefault(slug, Lane(slug))
            lane.flows = [f.strip() for f in cells[1].split(",")
                          if f.strip() and f.strip() != "—"]
            m = UUID_RE.search(cells[2])
            if m:
                lane.chat_id = m.group(0)
            lane.lead = cells[3]
            continue
        m = re.match(r"- \*\*([a-z0-9\-]+)\*\*\s*→\s*`([^`]+)`", s)
        if m:
            slug, path = m.group(1), m.group(2)
            lane = lanes.setdefault(slug, Lane(slug))
            rel = path.replace(HOME, "~").lstrip("~/")
            if rel.startswith("workspace/"):
                rel = rel[len("workspace/"):]
                repo_rel = f"workspace/{rel}"
            else:
                repo_rel = rel
            if repo_rel not in lane.band_candidates:
                lane.band_candidates.append(repo_rel)
            fm = re.match(r"workspace/flows/([^/]+)/", repo_rel)
            if fm and fm.group(1) not in lane.flows:
                lane.flows.append(fm.group(1))
    # derive record + band paths
    for slug, lane in lanes.items():
        if lane.chat_id:
            seat = f"side-chats/{lane.chat_id}/LANE_MEMORY.md"
            lane.record_paths.append(seat)
            if seat not in lane.band_candidates:
                lane.band_candidates.insert(0, seat)
        page = f"memory/lanes/{slug}.md"
        lane.record_paths.append(page)
        for flow in lane.flows:
            fp = f"workspace/flows/{flow}/LANE_MEMORY.md"
            lane.record_paths.append(fp)
            if fp not in lane.band_candidates:
                lane.band_candidates.append(fp)
    # Shared-chat primacy: several INDEX lanes may name one chat
    # (a seed seat). The seat file is the PRIMARY lane's band (first
    # in INDEX order) and the primary lane's property home; every
    # other lane sharing the chat falls through to its own flow
    # files — one seat file must never render as two lanes' bands,
    # nor exclude a lane by another lane's marking.
    primary = {}
    for slug, lane in lanes.items():
        if not lane.chat_id:
            continue
        seat = f"side-chats/{lane.chat_id}/LANE_MEMORY.md"
        if lane.chat_id not in primary:
            primary[lane.chat_id] = slug
        elif primary[lane.chat_id] != slug:
            lane.band_candidates = [c for c in lane.band_candidates
                                    if c != seat]
            lane.record_paths = [c for c in lane.record_paths
                                 if c != seat]
    return lanes


def resolve_inclusion(repo, head):
    """Condition 3: inclusion resolves from the lane's OWN property,
    INDEX-resolved, evaluated at HEAD, the read set built before any
    lane file opens. Returns (all_lanes, included_lanes). The
    property test never ingests an excluded lane's bytes."""
    index_text = repo.show(head, "memory/lanes/INDEX.md")
    lanes = parse_index(index_text or "")
    tree = repo.ls_tree(head)
    for slug, lane in lanes.items():
        for rec in lane.record_paths:
            if rec in tree and repo.prop_at(head, rec):
                lane.excluded = True
                break
    included = {s: l for s, l in lanes.items() if not l.excluded}
    return lanes, included


def lane_home_prefixes(lane):
    """Path prefixes (repo-relative and workspace-relative spellings)
    that belong to a lane's home — the references rule's test set."""
    prefs = set()
    if lane.chat_id:
        prefs.add(f"side-chats/{lane.chat_id}/")
        prefs.add(f"side-chats/{lane.chat_id}")
    prefs.add(f"memory/lanes/{lane.slug}.md")
    for flow in lane.flows:
        prefs.add(f"workspace/flows/{flow}/")
        prefs.add(f"flows/{flow}/")
    return prefs


# ------------------------------------------------------------------
# the band: parsing a LANE_MEMORY (schema states per DESIGN SS7)
# ------------------------------------------------------------------

QUEUE_HEADING = re.compile(r"next|in progress|blocked|queue|taps", re.I)
DID_HEADING = re.compile(r"just did", re.I)
TOKEN_RE = re.compile(r"→\s*([^·|()\[\];]+)")
BLOCKED_RE = re.compile(r"blocked-on:\s*([^·;|)]+)", re.I)
CYCLE_RE = re.compile(r"\b([a-z]{1,3}\d{2}(?:\.\d+)?)\b")
PACKET_RE = re.compile(r"packet:?\s*(\d{4})(?:\s*@\s*([a-z][a-z0-9\-]*))?",
                       re.I)
TAP_RE = re.compile(r"tap:\s*([a-z0-9][a-z0-9\-]{2,})", re.I)
PATH_TOKEN_RE = re.compile(
    r"(~/[^\s`'\"\)\],]+|(?:workspace/)?flows/[^\s`'\"\)\],]+"
    r"|side-chats/[^\s`'\"\)\],]+|memory/[^\s`'\"\)\],]+)")
STUB_RE = re.compile(r"lane-memory-pointer")


def parse_frontmatter(text):
    fm = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            for ln in text[3:end].splitlines():
                m = re.match(r"^([a-zA-Z_\-]+):\s*(.*)$", ln)
                if m:
                    fm[m.group(1).lower()] = m.group(2).strip()
    return fm


def schema_state(text, fm):
    if STUB_RE.search(text[:600]) or fm.get("type") == "lane-memory-pointer":
        return "stub"
    if fm.get("schema"):
        return fm["schema"]
    m = re.search(r"<!--\s*lane-schema:\s*(\d)", text[:600])
    if m:
        return m.group(1)
    if fm:
        return "2"
    return "prose"


class Item:
    def __init__(self, text):
        self.text = " ".join(text.split())
        self.token = None
        m = TOKEN_RE.search(self.text)
        if m:
            self.token = m.group(1).strip().rstrip("—-").strip()
        self.blocked_on = None
        m = BLOCKED_RE.search(self.text)
        if m:
            self.blocked_on = m.group(1).strip()
        self.citations = extract_citations(self.text)
        self.key = item_key(self.text)
        self.line_hash = hashlib.sha1(self.text.encode()).hexdigest()[:12]


def strip_volatile(text):
    """Remove the assignment + blocked-on segments ENTIRELY, so an
    item's key survives its own flips (a blocker clearing or a token
    changing must not make the item a stranger to itself)."""
    t = BLOCKED_RE.sub("", text)
    t = TOKEN_RE.sub("", t)
    t = re.sub(r"[—·|]+", " ", t)
    return " ".join(t.lower().split()).strip(" -")


def item_key(text):
    stripped = strip_volatile(text)
    cites = extract_citations(stripped)
    basis = "|".join(sorted(c["raw"] for c in cites)) + \
        "::" + stripped
    return hashlib.sha1(basis.encode()).hexdigest()[:10]


def extract_citations(text):
    cites = []
    for m in PACKET_RE.finditer(text):
        cites.append({"kind": "packet", "num": m.group(1),
                      "desk": m.group(2), "raw": m.group(0),
                      "pos": m.start()})
    seen_pkt_spans = [c["pos"] for c in cites]
    for m in CYCLE_RE.finditer(text):
        if any(abs(m.start() - p) < 8 for p in seen_pkt_spans):
            continue
        cites.append({"kind": "cycle", "id": m.group(1), "raw": m.group(0),
                      "pos": m.start()})
    for m in TAP_RE.finditer(text):
        cites.append({"kind": "tap", "name": m.group(1), "raw": m.group(0),
                      "pos": m.start()})
    for m in PATH_TOKEN_RE.finditer(text):
        cites.append({"kind": "path", "path": m.group(1).rstrip(".,;:"),
                      "raw": m.group(1), "pos": m.start()})
    return cites


class Band:
    def __init__(self, text, path):
        self.path = path
        self.text = text
        self.fm = parse_frontmatter(text)
        self.state = schema_state(text, self.fm)
        self.status = self.fm.get("status", "")
        self.queue = []      # Item list from NEXT/In progress/Blocked
        self.did = []        # Item list from JUST DID
        self.stub_target = None
        if self.state == "stub":
            m = re.search(r"`((?:~/|workspace/|side-chats/|memory/)[^`]+)`",
                          text)
            if m:
                self.stub_target = m.group(1)
            return
        cur = None
        for ln in text.splitlines():
            h = re.match(r"^##\s+(.*)$", ln)
            if h:
                cur = h.group(1)
                continue
            if cur is None:
                continue
            if ln.startswith("- "):
                if QUEUE_HEADING.search(cur):
                    self.queue.append(Item(ln[2:]))
                elif DID_HEADING.search(cur):
                    self.did.append(Item(ln[2:]))
            elif ln.startswith("  ") and ln.strip():
                # wrapped continuation of the previous item
                tgt = None
                if QUEUE_HEADING.search(cur):
                    tgt = self.queue
                elif DID_HEADING.search(cur):
                    tgt = self.did
                if tgt:
                    prev = tgt[-1]
                    merged = Item(prev.text + " " + ln.strip())
                    tgt[-1] = merged

    def parseable(self):
        return self.state != "stub" and bool(self.queue or self.did
                                            or self.fm)


def band_at(repo, sha, path, tree=None):
    text = repo.show(sha, path)
    if text is None:
        return None
    return Band(text, path)


def resolve_band(repo, sha, lane, tree, excluded_prefixes=()):
    """Pick the lane's band at sha, following a pointer stub under
    the property rules. Returns (band, note) where note is one of:
    'ok' · 'followed' · 'stub-unfollowed' · 'missing' · 'unparseable'.
    A stub target under an excluded home is never opened — it
    renders AS a stub (condition 2 + condition 3)."""
    for cand in lane.band_candidates:
        if cand not in tree:
            continue
        band = band_at(repo, sha, cand, tree)
        if band is None:
            continue
        fm_lane = band.fm.get("lane")
        if fm_lane and fm_lane != lane.slug:
            continue  # a file that names another lane is not this
            # lane's band, whatever directory it sits in
        if band.state != "stub":
            if band.parseable():
                return band, "ok"
            return band, "unparseable"
        # pointer stub: try to follow
        tgt = band.stub_target
        if not tgt:
            return band, "stub-unfollowed"
        rel = tgt.replace(HOME, "~")
        if rel.startswith("~/"):
            rel = rel[2:]
        repo_rel = rel
        if any(repo_rel == p.rstrip("/") or repo_rel.startswith(p)
               for p in excluded_prefixes):
            return band, "stub-unfollowed"
        if repo_rel not in tree:
            return band, "stub-unfollowed"
        target_band = band_at(repo, sha, repo_rel, tree)
        if target_band is None or target_band.state == "stub":
            return band, "stub-unfollowed"
        followed = target_band
        followed.path = repo_rel
        return followed, "followed"
    return None, "missing"


# ------------------------------------------------------------------
# the references rule (condition 4): pointer-withheld rendering
# ------------------------------------------------------------------

def withhold(text, excluded_prefixes):
    """Replace any path token resolving into an excluded home with a
    withheld marker. Returns (rendered_text, withheld_bool). Applied
    at extraction (board) AND at the ping composer (ledger)."""
    hit = False

    def repl(m):
        nonlocal hit
        tok = m.group(1)
        norm = tok.replace(HOME, "~")
        if norm.startswith("~/"):
            norm = norm[2:]
        for pref in excluded_prefixes:
            if norm == pref.rstrip("/") or norm.startswith(pref):
                hit = True
                return "(pointer withheld)"
        return tok

    return PATH_TOKEN_RE.sub(repl, text), hit


# ------------------------------------------------------------------
# cited-record resolution (C7's machinery; the calibration's method,
# R1-R6 applied). Records live on disk: cycles + taps under the
# workspace root, packets under the desks roots. States are read
# live — the present state of the record the queue cites.
# ------------------------------------------------------------------

# R2: closedness is read from the status FIELD through this table —
# a value is closed iff it STARTS with a closed word ("BRIEF
# complete" starts with a phase word and is NOT closed;
# "closed-pass-with-deviation" starts with "closed" and is).
CLOSED_STARTS = ("done", "closed", "complete", "completed", "decided",
                 "cancelled", "canceled", "discharged")
# R5: the self-state vocabulary — a line whose citation segment
# carries one of these records its own state and is not a finding.
SELF_STATE = re.compile(
    r"\b(passed|decided|ruled|done|closed|complete|completed|landed"
    r"|delivered|discharged|cancelled|canceled|knowingly|re-ran"
    r"|re-run|rerun)\b",
    re.I)
STATUS_RE = re.compile(r"status[:\s]+([^\n]{0,60})", re.I)


def status_field(text, cited_id=None):
    """(found, value, closed) from a record's head. The status FIELD
    rules (R2); a title close counts only when the heading names the
    cited record itself (R4)."""
    if text is None:
        return (False, None, False)
    head = "\n".join(text.splitlines()[:40])
    m = STATUS_RE.search(head)
    if m:
        value = m.group(1).strip().strip("*`").strip()
        low = value.lower()
        closed = any(low == w or low.startswith(w + " ")
                     or low.startswith(w + "-") or low.startswith(w + "—")
                     for w in CLOSED_STARTS)
        return (True, value, closed)
    if cited_id:
        for ln in head.splitlines():
            if ln.startswith("#") and cited_id.lower() in ln.lower() \
                    and re.search(r"\b(CLOSED|COMPLETE|DONE)\b", ln, re.I):
                return (True, "closed (title)", True)
    return (False, None, False)


class Records:
    """Live cited-record states: cycles (workspace), taps
    (workspace), packets (desks). Built once per run."""

    def __init__(self, workspace_root, desks_roots, home=None):
        self.ws = workspace_root
        self.home = home or HOME
        self.desk_roots = desks_roots
        self._cycles = None      # flow -> {id: (closed, path, value)}
        self._taps = None        # name -> (closed, path, value)
        self._packets = None     # desk -> {num: (closed, where)}

    # ---- cycles: R1 flow-scoped, R6 exact-id ----
    def cycles(self):
        if self._cycles is not None:
            return self._cycles
        out = {}
        flows_dir = os.path.join(self.ws, "flows")
        if os.path.isdir(flows_dir):
            for flow in sorted(os.listdir(flows_dir)):
                fdir = os.path.join(flows_dir, flow)
                if not os.path.isdir(fdir):
                    continue
                d = {}
                for sub in sorted(os.listdir(fdir)):
                    cpath = os.path.join(fdir, sub, "cycle.md")
                    if not os.path.isfile(cpath):
                        cpath = os.path.join(fdir, sub, "CYCLE.md")
                    if not os.path.isfile(cpath):
                        continue
                    cid = sub.split("-")[0].lower()
                    try:
                        text = open(cpath, errors="replace").read()
                    except OSError:
                        continue
                    found, value, closed = status_field(text, cid)
                    if cid not in d or closed:
                        d[cid] = (closed, cpath, value)
                out[flow] = d
        self._cycles = out
        return out

    def cycle_state(self, flow, cid):
        """(resolved, closed, where, value). R1: only the citing
        lane's OWN flow is searched — mentions never widen scope.
        R6: the id key is exact, sub-cycles included; no parent
        fallback, ever."""
        d = self.cycles().get(flow, {})
        if cid in d:
            closed, path, value = d[cid]
            return (True, closed, path, value)
        return (False, False, None, None)

    # ---- taps ----
    def taps(self):
        if self._taps is not None:
            return self._taps
        out = {}
        flows_dir = os.path.join(self.ws, "flows")
        if os.path.isdir(flows_dir):
            for flow in sorted(os.listdir(flows_dir)):
                tdir = os.path.join(flows_dir, flow, "taps")
                if not os.path.isdir(tdir):
                    continue
                for name in sorted(os.listdir(tdir)):
                    if not name.endswith(".md"):
                        continue
                    path = os.path.join(tdir, name)
                    try:
                        text = open(path, errors="replace").read()
                    except OSError:
                        continue
                    found, value, closed = status_field(text)
                    out[name[:-3].lower()] = (closed, path, value)
        self._taps = out
        return out

    def tap_state(self, name):
        t = self.taps().get(name.lower())
        if t is None:
            return (False, False, None, None)
        closed, path, value = t
        return (True, closed, path, value)

    # ---- packets: R3 per-desk keys ----
    def packets(self):
        if self._packets is not None:
            return self._packets
        out = {}
        states_closed = ("completed", "ledger")
        states_all = ("completed", "ledger", "in-progress", "backlog",
                      "inbox", "routed", "modelling")
        for root in self.desk_roots:
            if not os.path.isdir(root):
                continue
            for desk in sorted(os.listdir(root)):
                ddir = os.path.join(root, desk)
                if not os.path.isdir(ddir):
                    continue
                d = out.setdefault(desk, {})
                for state in states_all:
                    sdir = os.path.join(ddir, state)
                    if not os.path.isdir(sdir):
                        continue
                    for name in sorted(os.listdir(sdir)):
                        num = name.split("-")[0]
                        if num.isdigit() and num not in d:
                            d[num] = (state in states_closed,
                                      f"{desk}/{state}/{name}")
        self._packets = out
        return out

    def packet_state(self, num, desk, citing_desk):
        """R3: the desk is part of the citation. A bare number
        resolves only against the citing lane's own desk context;
        without one it is C7-silent — never cross-desk matched."""
        pk = self.packets()
        use = desk or citing_desk
        if not use:
            return (False, False, None, None)
        d = pk.get(use, {})
        if num in d:
            closed, where = d[num]
            return (True, closed, where, None)
        return (False, False, None, None)

    # ---- path citations: R4 the cited record's OWN state ----
    def path_state(self, raw_path, home):
        p = raw_path.replace("~", home).rstrip(".,;:")
        if not os.path.isfile(p):
            return (False, False, None, None)
        try:
            text = open(p, errors="replace").read()
        except OSError:
            return (False, False, None, None)
        base = os.path.basename(os.path.dirname(p)).split("-")[0].lower()
        found, value, closed = status_field(text, base)
        if not found:
            return (True, False, p, None)
        return (True, closed, p, value)


def segment_at(text, pos):
    """The line segment a citation sits in (split on ; · | and ', ')
    — R5's presentation test is scoped to the citation's own
    segment, so 'waves 1+2 done' after a comma does not exempt the
    'm03 wave 3 WAITING' segment that cites it."""
    start = 0
    for sep in (";", "·", "|", ", "):
        i = text.rfind(sep, 0, pos)
        if i >= start:
            start = i + len(sep) if sep == ", " else i + 1
    end = len(text)
    for sep in (";", "·", "|", ", "):
        i = text.find(sep, pos)
        if i != -1 and i < end:
            end = i
    return text[start:end]


def resolve_citation(records, lane, cite, citing_desk):
    """-> (resolved, closed, evidence_str). One citation, resolved
    per its kind under R1-R6."""
    kind = cite["kind"]
    if kind == "cycle":
        for flow in lane.flows:
            resolved, closed, where, value = records.cycle_state(
                flow, cite["id"])
            if resolved:
                return (True, closed,
                        f"cycle {cite['id']} @ {where} "
                        f"(status: {value})")
        return (False, False, None)
    if kind == "packet":
        resolved, closed, where, _ = records.packet_state(
            cite["num"], cite.get("desk"), citing_desk)
        if resolved:
            state = "closed" if closed else "open"
            return (True, closed,
                    f"packet {cite['num']} @ {where} ({state})")
        return (False, False, None)
    if kind == "tap":
        resolved, closed, where, value = records.tap_state(cite["name"])
        if resolved:
            return (True, closed,
                    f"tap {cite['name']} @ {where} (status: {value})")
        return (False, False, None)
    if kind == "path":
        resolved, closed, where, value = records.path_state(
            cite["path"], records.home)
        if resolved and closed:
            return (True, True,
                    f"path {cite['path']} (status: {value})")
        if resolved:
            return (True, False, None)
        return (False, False, None)
    return (False, False, None)


def c7_pairs(records, lane, band, citing_desk):
    """The checker leg for one lane: (pairs, resolved_count,
    cited_count). A pair = a queue line presenting a CLOSED record
    as live work; the line's own segment carrying a self-state word
    (R5) is not a finding."""
    pairs, resolved, cited = [], 0, 0
    for item in band.queue:
        for cite in item.citations:
            cited += 1
            res, closed, evidence = resolve_citation(
                records, lane, cite, citing_desk)
            if res:
                resolved += 1
            if res and closed:
                seg = segment_at(item.text, cite["pos"])
                if SELF_STATE.search(seg):
                    continue
                pairs.append({"line": item.text, "evidence": evidence,
                              "cite": cite["raw"]})
    return pairs, resolved, cited


# ------------------------------------------------------------------
# C2 — relative freshness (a prompt, never a finding; Q-7: both ages
# shown, no numeric flag at v1)
# ------------------------------------------------------------------

# Bulk machinery that touches band files without a seat moving its
# queue — sampled from the live tree's subjects, 2026-11-04 (schema
# conversions, lean/prune passes, regenerations). A band touch whose
# subject matches is not a seat move of the band.
BULK_BAND = re.compile(
    r"schema v\d+ conversion|lean pass|prune|regeneration", re.I)


def is_compiler_commit(repo, sha, paths, subject):
    if subject.startswith(COMPILER_SUBJECT_PREFIX):
        return True
    return bool(paths) and all(p.startswith(BOARD_SUBTREE) for p in paths)


def c2_prompt(repo, lane, band_path):
    """(prompt_dict | None): the lane's own activity outside its band
    is newer than the band's last seat move. Both ages ride the
    prompt line. Activity is measured with the band file itself
    pathspec-excluded, so a band move is never its own anomaly."""
    home_paths = []
    if lane.chat_id:
        home_paths.append(f"side-chats/{lane.chat_id}")
    for flow in lane.flows:
        home_paths.append(f"workspace/flows/{flow}")
    home_paths.append(f"memory/lanes/{lane.slug}.md")
    band_moves = [c for c in repo.log_touching(band_path, 12)
                  if not BULK_BAND.search(c["subject"])]
    band_last = band_moves[0]["date"] if band_moves else None
    out = repo.git("log", "-1", "--format=%cI", "--", *home_paths,
                   f":(exclude){band_path}", check=False).stdout
    active_last = out.strip() or None
    if active_last and band_last and active_last > band_last:
        return {"band_last": band_last, "active_last": active_last}
    if active_last and not band_last:
        return {"band_last": None, "active_last": active_last}
    return None


# ------------------------------------------------------------------
# assignment resolution (A1): a token names a seat of record,
# INDEX-resolvable — or it is a C7-class finding, never a ping
# target (N2).
# ------------------------------------------------------------------

def resolve_assignee(token, lanes, default_lane=None):
    """-> Lane | None. Resolution order: exact slug · chat id · the
    INDEX lead cell naming the token (or named by it)."""
    if token is None:
        return default_lane
    t = token.strip()
    if not t:
        return default_lane
    low = t.lower()
    for slug, lane in lanes.items():
        if low == slug.lower():
            return lane
        if lane.chat_id and low == lane.chat_id.lower():
            return lane
    for slug, lane in lanes.items():
        lead = lane.lead.lower()
        if lead and (low in lead or lead in low):
            return lane
    return None


# ------------------------------------------------------------------
# the ledger (append-only JSONL; state derived by folding)
# ------------------------------------------------------------------

def fold_ledger(text):
    events = []
    if text:
        for ln in text.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                events.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
    return events


def ledger_state(events):
    """-> (pinged: {flip_id: event}, flips: int, closes: int).
    A ping is open until a clear event names it."""
    pinged, flips, closes = {}, 0, 0
    for ev in events:
        k = ev.get("kind")
        if k == "ping":
            pinged[ev["flip_id"]] = ev
            flips += 1
        elif k == "superseded":
            flips += 1
        elif k == "close":
            closes += 1
        elif k == "clear":
            pinged.pop(ev.get("flip_id"), None)
    return pinged, flips, closes


# ------------------------------------------------------------------
# the board's own state: stamp + the blocked-open snapshot ride the
# board file (header + a machine footer), so the two named files
# (board + ledger) carry everything the next compile needs.
# ------------------------------------------------------------------

def board_stamp(board_text):
    if not board_text:
        return None
    m = re.search(r"^compiled-through:\s*([0-9a-f]{40})\s*$", board_text,
                  re.M)
    return m.group(1) if m else None


def board_snapshot(board_text):
    if not board_text:
        return {}
    m = re.search(r"<!-- board-state: (\{.*?\}) -->", board_text, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return {}


# ------------------------------------------------------------------
# flip extraction: the interval walk (condition 6) + the
# predecessor-close state comparison (A2a)
# ------------------------------------------------------------------

def diff_band_flips(lane_slug, before, after, commit, lanes):
    """Flips + closes from one band file's before/after at one
    commit. Returns event dicts (kind: ping-candidate | close)."""
    out = []
    bq = {i.key: i for i in (before.queue if before else [])}
    aq = {i.key: i for i in (after.queue if after else [])}
    bd = {i.key: i for i in (before.did if before else [])}
    ad = {i.key: i for i in (after.did if after else [])}
    for key, item in aq.items():
        old = bq.get(key)
        if old is None:
            # a written assignment landing is a record event (A2b);
            # a tokenless arrival defaults to the lane's own lead
            # and is not a ping (the board carries it).
            if item.token:
                out.append({"ev": "flip", "kind": "assignment",
                            "lane": lane_slug, "item": item,
                            "sha": commit["sha"]})
        else:
            if item.token != old.token and (item.token or old.token):
                # a token change — including removal, which hands the
                # move back to the lane's own lead (A1's default)
                out.append({"ev": "flip", "kind": "assignment-flip",
                            "lane": lane_slug, "item": item,
                            "sha": commit["sha"]})
            if old.blocked_on and not item.blocked_on:
                out.append({"ev": "flip", "kind": "dependency-landed",
                            "lane": lane_slug, "item": item,
                            "sha": commit["sha"],
                            "pred": old.blocked_on})
    for key, item in bq.items():
        if key in aq:
            continue
        # left the queue: a hand-off (predecessor close, A2c) when a
        # same-commit JUST DID line shares its citation and names a
        # successor; otherwise a close (A5's denominator).
        successor = None
        item_cites = {c["raw"] for c in item.citations}
        for dkey, ditem in ad.items():
            if dkey in bd:
                continue
            dcites = {c["raw"] for c in ditem.citations}
            if item_cites and item_cites & dcites and ditem.token:
                successor = ditem
                break
        if successor is not None:
            out.append({"ev": "flip", "kind": "predecessor-close",
                        "lane": lane_slug, "item": successor,
                        "closed_item": item, "sha": commit["sha"]})
        else:
            out.append({"ev": "close", "lane": lane_slug, "item": item,
                        "sha": commit["sha"]})
    return out


def walk_flips(repo, stamp, head0, included, tree0):
    """Replay the interval stamp..head0 over the included lanes'
    band paths only (exclusion layer 2: an excluded lane's commits
    are never even walked). Flips return in stem order."""
    pathspecs = []
    owner = {}   # band path -> (lane, candidate path)
    for slug, lane in included.items():
        for cand in lane.band_candidates:
            pathspecs.append(cand)
            owner[cand] = (slug, cand)
    if not pathspecs:
        return [], []
    commits = repo.log_range(stamp, head0, pathspecs)
    events, seen = [], set()
    for commit in commits:
        if is_compiler_commit(repo, commit["sha"], commit["paths"],
                              commit["subject"]):
            continue
        for path in commit["paths"]:
            if path not in owner:
                continue
            slug, _ = owner[path]
            before = band_at(repo, f"{commit['sha']}^", path)
            after = band_at(repo, commit["sha"], path)
            for ev in diff_band_flips(slug, before, after, commit,
                                      included):
                if ev["ev"] == "flip":
                    dedupe = (slug, ev["item"].key, ev["kind"],
                              ev["item"].token, commit["sha"])
                    if dedupe in seen:
                        continue
                    seen.add(dedupe)
                events.append(ev)
    return events, commits


def pred_key(blocked_on):
    """The predecessor's identity AS A HASH — the raw reference may
    point into an excluded home, and the key rides the board's
    state footer and the ledger's flip ids, where an excluded
    pointer must never ride (condition 4 at the state layer)."""
    cites = extract_citations(blocked_on or "")
    raw = cites[0]["raw"] if cites else \
        " ".join((blocked_on or "").lower().split())[:60]
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


def dependency_flips(records, lane, band, prev_snapshot, citing_desk):
    """A2a by state comparison: a line still blocked on a predecessor
    that was OPEN at the previous compile and is CLOSED now is a
    dependency-landed flip. The snapshot rides the previous board;
    the flip identity is content-keyed (lane|item|pred), so it can
    never re-fire for the same predecessor."""
    flips, snapshot = [], {}
    for item in band.queue:
        if not item.blocked_on:
            continue
        pk = pred_key(item.blocked_on)
        skey = f"{lane.slug}|{item.key}|{pk}"
        cites = extract_citations(item.blocked_on)
        closed_now = False
        if cites:
            res, closed, _ = resolve_citation(records, lane, cites[0],
                                              citing_desk)
            closed_now = bool(res and closed)
        if closed_now:
            if prev_snapshot.get(skey) == "open":
                flips.append({"ev": "flip", "kind": "dependency-landed",
                              "lane": lane.slug, "item": item,
                              "sha": None, "pred": item.blocked_on,
                              "pred_key": pk})
            snapshot[skey] = "closed"
        else:
            snapshot[skey] = "open"
    return flips, snapshot


# ------------------------------------------------------------------
# view assembly: everything a render needs, computed once from HEAD
# objects (bands + inclusion) and live record states (C7/C2).
# ------------------------------------------------------------------

class View:
    pass


def build_view(repo, head0, records):
    v = View()
    v.head = head0
    v.all_lanes, v.included = resolve_inclusion(repo, head0)
    v.tree = repo.ls_tree(head0)
    v.excluded_prefixes = set()
    for slug, lane in v.all_lanes.items():
        if lane.excluded:
            v.excluded_prefixes |= lane_home_prefixes(lane)
    v.entries = {}       # slug -> entry dict
    v.total_lines = 0
    v.resolved_lines = 0
    for slug, lane in sorted(v.included.items()):
        band, note = resolve_band(repo, head0, lane, v.tree,
                                  v.excluded_prefixes)
        entry = {"lane": lane, "band": band, "note": note, "pairs": [],
                 "c2": None, "unresolvable": [], "withheld_lines": 0}
        if band is not None and note in ("ok", "followed"):
            pairs, resolved, cited = c7_pairs(records, lane, band, None)
            entry["pairs"] = pairs
            v.total_lines += len(band.queue)
            v.resolved_lines += sum(
                1 for it in band.queue
                if any(resolve_citation(records, lane, c, None)[0]
                       for c in it.citations))
            for item in band.queue:
                if item.token and resolve_assignee(
                        item.token, v.included) is None:
                    entry["unresolvable"].append(item)
                _, hit = withhold(item.text, v.excluded_prefixes)
                if hit:
                    entry["withheld_lines"] += 1
            entry["c2"] = c2_prompt(repo, lane, band.path)
        v.entries[slug] = entry
    # awaiting state, folded from the ledger at HEAD
    ledger_text = repo.show(head0, LEDGER_PATH)
    v.ledger_events = fold_ledger(ledger_text)
    v.open_pings, v.flip_count, v.close_count = ledger_state(
        v.ledger_events)
    v.prev_board = repo.show(head0, BOARD_PATH)
    v.prev_stamp = board_stamp(v.prev_board)
    v.prev_snapshot = board_snapshot(v.prev_board)
    return v


def render_board(v, stamp, snapshot, sweep_touched, compiled_at):
    total = v.total_lines or 0
    share = (100.0 * v.resolved_lines / total) if total else 0.0
    ratio = f"{v.flip_count}:{v.close_count}" if v.close_count \
        else f"{v.flip_count}:0"
    lines = []
    lines.append("# Rolling board — compiled from the memory tree")
    lines.append("")
    lines.append(
        "_What this board proves: C7 citation pairs — a queue line "
        "presenting a record its own citation shows closed — and C2 "
        "freshness prompts: a band older than its lane's own "
        "activity, a prompt to look, never a finding of disagreement. "
        "A queue is graded only against the records it cites; "
        "nothing else is claimed._")
    lines.append("")
    lines.append(
        f"coverage: C7-checkable {share:.0f}% of rendered queue "
        f"lines ({v.resolved_lines}/{total} lines carry a resolved "
        f"citation) · sweep-touched lanes in interval: "
        f"{sweep_touched}")
    lines.append(f"compiled-through: {stamp}")
    lines.append(f"compiled-at: {compiled_at}")
    lines.append(
        f"flip:close (ledger lifetime): flips {v.flip_count} · "
        f"closes {v.close_count} · ratio {ratio}")
    lines.append("")
    pings_by_lane = {}
    for fid, ev in v.open_pings.items():
        pings_by_lane.setdefault(ev.get("lane"), []).append(ev)
    for slug in sorted(v.entries):
        entry = v.entries[slug]
        lane, band, note = entry["lane"], entry["band"], entry["note"]
        lead = f" — {lane.lead}" if lane.lead else ""
        if note == "missing":
            lines.append(f"## {slug}{lead}")
            lines.append("- state: no LANE_MEMORY in the tree — a "
                         "state line, not an empty queue")
            lines.append("")
            continue
        state = band.state if band else "?"
        if note == "stub-unfollowed":
            tgt = band.stub_target or "(target unnamed)"
            lines.append(f"## {slug}{lead} · schema: stub")
            lines.append(f"- queue held behind a pointer stub: "
                         f"{tgt} — rendered AS a stub, never as an "
                         f"empty queue")
            lines.append("")
            continue
        if note == "unparseable":
            lines.append(f"## {slug}{lead} · schema: {state}")
            lines.append("- state: band present but not parseable "
                         "(no recognisable queue band) — a state "
                         "line, not an empty queue")
            lines.append("")
            continue
        status = band.status
        suffix = f" · status: {status}" if status else ""
        src = f" · band: {band.path}" if note == "followed" else ""
        lines.append(f"## {slug}{lead} · schema: {state}{suffix}{src}")
        if status in ("dormant", "parked-by-design"):
            lines.append(f"- state: {status} — a state line, not a "
                         f"queue")
        else:
            for item in band.queue:
                text, _ = withhold(item.text, v.excluded_prefixes)
                lines.append(f"- {text}")
            if not band.queue:
                lines.append("- (queue empty as written)")
        for p in entry["pairs"]:
            text, _ = withhold(p["line"], v.excluded_prefixes)
            lines.append(f"- ⚠ C7 pair: {text} ↔ {p['evidence']}")
        if entry["c2"]:
            c2 = entry["c2"]
            lines.append(
                f"- C2 prompt: band last moved {c2['band_last'] or '—'}"
                f" · lane last active {c2['active_last']} — a prompt "
                f"to look, not a finding")
        for item in entry["unresolvable"]:
            lines.append(
                f"- ⚠ unresolvable assignment: → {item.token} on "
                f"“{item.text[:80]}” — a finding (A1), never a ping "
                f"target")
        for ev in pings_by_lane.get(slug, []):
            age = ""
            try:
                t0 = datetime.strptime(ev["ts"], "%Y-%m-%dT%H:%M:%SZ")
                age = age_str((datetime.now(timezone.utc) -
                               t0.replace(tzinfo=timezone.utc)
                               ).total_seconds())
            except Exception:
                pass
            lines.append(
                f"- awaiting: {ev.get('item', '')[:100]} → "
                f"{ev.get('assignee', {}).get('slug') or ev.get('assignee', {}).get('token', '')}"
                f" · pinged {ev.get('ts', '')} · age {age}")
        lines.append("")
    snap = json.dumps(snapshot, sort_keys=True)
    lines.append(f"<!-- board-state: {snap} -->")
    lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------
# ping composition (the composer applies the references rule too —
# condition 4 at both ends)
# ------------------------------------------------------------------

def compose_events(v, raw_events, head0):
    """raw walk/pred events -> ledger events (ping · superseded ·
    close · clear), with idempotence checked against the HEAD
    ledger ∪ this run's own compositions (N5: the within-run
    duplicate class is empty by flip-identity construction — the
    walk visits each commit once — and the HEAD check bounds the
    crash residue to the crashed run's own flips)."""
    ledger_ids = {ev.get("flip_id") for ev in v.ledger_events
                  if ev.get("flip_id")}
    composed = []
    closed_keys = [(ev["lane"], ev["item"].key) for ev in raw_events
                   if ev["ev"] == "close"]
    for ev in raw_events:
        if ev["ev"] == "close":
            composed.append({"kind": "close", "ts": now_iso(),
                             "lane": ev["lane"], "item_key":
                             ev["item"].key, "sha": ev["sha"]})
            continue
        item = ev["item"]
        lane = v.included[ev["lane"]]
        if ev["kind"] == "predecessor-close":
            ping_item = ev["closed_item"]
        else:
            ping_item = item
        token = item.token
        assignee = resolve_assignee(token, v.included,
                                    default_lane=lane)
        if token and assignee is None:
            continue  # unresolvable: a board finding, never a ping
        if ev.get("pred_key"):
            flip_id = f"{ev['lane']}:{ping_item.key}:{ev['kind']}:" \
                      f"{ev['pred_key']}"
        else:
            flip_id = f"{ev['lane']}:{ping_item.key}:{ev['kind']}:" \
                      f"{(ev['sha'] or head0)[:12]}"
        if flip_id in ledger_ids:
            continue
        ledger_ids.add(flip_id)
        text, _ = withhold(ping_item.text, v.excluded_prefixes)
        # the composer's half of condition 4: the citations the
        # ledger stores are withheld too — the ledger is a generated
        # file in the repo and never carries an excluded pointer.
        safe_cites = [withhold(c["raw"], v.excluded_prefixes)[0]
                      for c in ping_item.citations]
        record_ptr = safe_cites[0] if safe_cites else ping_item.key
        ping_text = (f"⚑ you're up — {ev['lane']} · {text} · "
                     f"record: {record_ptr} · trigger: {ev['kind']} "
                     f"@ {(ev['sha'] or head0)[:8]}")
        superseded = (ev["lane"], ping_item.key) in closed_keys
        composed.append({
            "kind": "superseded" if superseded else "ping",
            "flip_id": flip_id, "ts": now_iso(), "lane": ev["lane"],
            "item_key": ping_item.key, "item": text,
            "line_hash": ping_item.line_hash,
            "citations": safe_cites,
            "assignee": {"token": token,
                         "slug": assignee.slug if assignee else None,
                         "chat_id": assignee.chat_id
                         if assignee else None},
            "trigger": {"kind": ev["kind"], "record": record_ptr,
                        "sha": ev["sha"] or head0},
            "ping_text": ping_text})
    # awaiting clears: an open ping clears when its pointer line
    # moves — the item's line in its home lane changed or left, or
    # the assignee's queue picked the work up (citation match).
    for fid, ev in list(v.open_pings.items()):
        home = v.entries.get(ev.get("lane"))
        if not home or not home["band"] or \
                home["note"] not in ("ok", "followed"):
            continue
        band = home["band"]
        cur = next((i for i in band.queue
                    if i.key == ev.get("item_key")), None)
        cleared = False
        if ev.get("trigger", {}).get("kind") == "predecessor-close":
            aslug = ev.get("assignee", {}).get("slug")
            aentry = v.entries.get(aslug) if aslug else None
            if aentry and aentry["band"]:
                cites = set(ev.get("citations", []))
                if any(cites & {c["raw"] for c in i.citations}
                       for i in aentry["band"].queue):
                    cleared = True
        else:
            if cur is None or cur.line_hash != ev.get("line_hash"):
                cleared = True
        if cleared:
            composed.append({"kind": "clear", "flip_id": fid,
                             "ts": now_iso(), "sha": head0})
    return composed


# ------------------------------------------------------------------
# the scan guard (packet 0018): the sweep's secret-scan patterns,
# imported live from the sweep's implementation — the pattern set
# has ONE source of truth (~/workspace/bin/memory-commit-sweep,
# SECRET_PATTERNS there) and this file carries no copy of it.
# The sweep module is import-guarded (its main runs only as
# __main__), so loading it costs constants + function defs only.
# The pattern source is the estate's installed sweep (the real
# HOME), independent of --repo: the guard travels with the
# committer, not with the repo under compile.
# ------------------------------------------------------------------

SWEEP_PATH = os.path.join(HOME, "workspace", "bin",
                          "memory-commit-sweep")
_sweep_patterns = None


def load_sweep_patterns():
    """[(name, pattern)] imported live from the sweep. Fails the
    run when the source is unreachable — a committer that cannot
    scan must not commit."""
    global _sweep_patterns
    if _sweep_patterns is not None:
        return _sweep_patterns
    import importlib.machinery
    import importlib.util
    try:
        loader = importlib.machinery.SourceFileLoader(
            "memory_commit_sweep", SWEEP_PATH)
        spec = importlib.util.spec_from_loader(
            "memory_commit_sweep", loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        patterns = list(mod.SECRET_PATTERNS)
        if not patterns:
            raise ValueError("SECRET_PATTERNS is empty")
    except Exception as e:
        write_refusal_alert(error=(
            f"secret-scan guard: cannot load the sweep's patterns "
            f"from {SWEEP_PATH} ({type(e).__name__}: {e})"))
        fail(f"secret-scan guard: cannot load the sweep's patterns "
             f"from {SWEEP_PATH} ({type(e).__name__}: {e}) — "
             f"refusing to commit unscanned")
    _sweep_patterns = patterns
    return patterns


def scan_composed(board_text, ledger_text):
    """[(repo-path, pattern-class)] for every sweep pattern class
    hitting the composed board or ledger. Same verdict as the
    sweep's scan_text (any hit refuses); every class is reported,
    not just the first. The matched VALUE is never extracted —
    only the class name rides the finding."""
    hits = []
    for path, text in ((BOARD_PATH, board_text),
                       (LEDGER_PATH, ledger_text)):
        for name, pat in load_sweep_patterns():
            if pat.search(text):
                hits.append((path, name))
    return hits


# ------------------------------------------------------------------
# the refusal alert (packet 0019): the sweep-alert.json shape,
# mirrored from ~/workspace/bin/memory-commit-sweep — its ALERT is
# DATA/sweep-alert.json under <workspace>/data/memory/, written as
# {"ts", "flagged": [{"file", "pattern"}]} when content is refused
# and {"ts", "error", "flagged"} on an operational error, and
# UNLINKED by the next pass that has nothing flagged: present only
# while something needs eyes. The compiler's alert is the same
# shape one data dir over — <workspace>/data/lane/board-alert.json,
# the workspace under compile (production ~/workspace; a fixture's
# staged workspace in tests). Written on the two refusals the scan
# guard can make — a hit, and an unloadable pattern source — AFTER
# the refusal decision and before the exit, so a failed alert
# write can never weaken the refusal (a stderr note; the refusal
# stands). A successful compile unlinks it, the sweep's lifecycle
# exactly. The matched value is never persisted: the alert carries
# file + pattern class, or the load cause — nothing else. ts is
# the compiler's own now_iso() (UTC), the clock every other record
# this tool writes already carries. The reader is the
# board-refusal-watch hook (caps/lane/board-refusal-watch.sh),
# which polls this file and wakes the lane's lead seat with the
# alert as its payload — the sweep's dedicated-hook relay pattern
# (the memory-commit-sweep hook cats sweep-alert.json into its
# wake payload the same way).
# ------------------------------------------------------------------

ALERT_REL = os.path.join("data", "lane", "board-alert.json")
_alert_path = None


def set_alert_path(workspace_root):
    global _alert_path
    _alert_path = os.path.join(workspace_root, ALERT_REL)


def write_refusal_alert(flagged=None, error=None):
    """Best-effort, post-decision mirror of the sweep's alert
    write. Never raises: an alert failure is a stderr note, and
    the refusal it describes stands either way."""
    if _alert_path is None:
        return
    record = {"ts": now_iso()}
    if error is not None:
        record["error"] = error
    record["flagged"] = flagged or []
    try:
        os.makedirs(os.path.dirname(_alert_path), exist_ok=True)
        with open(_alert_path, "w") as fh:
            fh.write(json.dumps(record, indent=1))
    except Exception as e:
        print(f"board-compiler: refusal alert write failed "
              f"({type(e).__name__}: {e}) — the refusal stands",
              file=sys.stderr)


def clear_refusal_alert():
    """The sweep's lifecycle: a clean pass unlinks the alert.
    Guarded the same way — hygiene never fails a landed write."""
    if _alert_path is None:
        return
    try:
        if os.path.exists(_alert_path):
            os.unlink(_alert_path)
    except Exception as e:
        print(f"board-compiler: refusal alert clear failed "
              f"({type(e).__name__}: {e})", file=sys.stderr)


# ------------------------------------------------------------------
# modes
# ------------------------------------------------------------------

def crash_point(name):
    """Test-only fault injection (stage 4's crash battery): die
    mid-compile at a named point so the stamp discipline is proven,
    not asserted."""
    if os.environ.get("BOARD_COMPILER_CRASH_AT") == name:
        os._exit(70)


def sweep_touched_lanes(commits, included):
    owner = {}
    for slug, lane in included.items():
        for cand in lane.band_candidates:
            owner[cand] = slug
    touched, swept = {}, {}
    for c in commits:
        for p in c["paths"]:
            slug = owner.get(p)
            if not slug:
                continue
            touched[slug] = True
            if c["subject"].rstrip().endswith("(sweep)"):
                swept[slug] = True
            else:
                swept[slug] = False
    names = sorted(s for s in touched if swept.get(s))
    return ", ".join(names) if names else "none"


def finish_view_counts(v, composed):
    events = v.ledger_events + composed
    v.open_pings, v.flip_count, v.close_count = ledger_state(events)


def do_write(repo, records):
    import fcntl
    gitdir = repo.git("rev-parse", "--absolute-git-dir").stdout.strip()
    lockf = open(os.path.join(gitdir, "board-compiler.lock"), "a+")
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        msg = "writer lock held — run deferred whole to the next tick"
        if JSON_MODE:
            print(json.dumps({"deferred": True, "reason": msg}))
        else:
            print(f"board-compiler: {msg}")
        return 0
    set_alert_path(records.ws)
    head0 = repo.head()
    v = build_view(repo, head0, records)
    stamp = v.prev_stamp
    rebaselined = stamp is not None and not repo.is_ancestor(stamp, head0)
    baseline = stamp is None or rebaselined
    raw_events, commits = [], []
    if not baseline:
        raw_events, commits = walk_flips(repo, stamp, head0, v.included,
                                         v.tree)
    crash_point("walk")
    new_snapshot = {}
    for slug, entry in v.entries.items():
        if entry["band"] and entry["note"] in ("ok", "followed"):
            flips, snap = dependency_flips(records, entry["lane"],
                                           entry["band"],
                                           v.prev_snapshot, None)
            raw_events.extend(flips)
            new_snapshot.update(snap)
    composed = compose_events(v, raw_events, head0)
    finish_view_counts(v, composed)
    touched = sweep_touched_lanes(commits, v.included) \
        if commits else "none (baseline)" if baseline else "none"
    rendered = render_board(v, head0, new_snapshot, touched, now_iso())
    crash_point("render")
    # ledger text: HEAD's ledger + this run's events, in one commit
    ledger_old = repo.show(head0, LEDGER_PATH) or ""
    lines = [ln for ln in ledger_old.splitlines() if ln.strip()]
    if not lines:
        lines.append(json.dumps({"kind": "genesis", "ts": now_iso(),
                                 "stamp": head0}))
    lines += [json.dumps(e, ensure_ascii=False) for e in composed]
    ledger_new = "\n".join(lines) + "\n"
    # no-op discipline: nothing in the interval, nothing composed,
    # board already at HEAD -> commit nothing (plan component 4).
    if not baseline and not commits and not composed:
        if JSON_MODE:
            print(json.dumps({"noop": True, "head": head0,
                              "stamp": stamp}))
        else:
            print(f"board: no interval events — nothing committed "
                  f"(stamp {stamp[:12] if stamp else '—'})")
        return 0
    # the scan guard (packet 0018): the sweep's own patterns over
    # the composed bytes, inside the lock, after composition,
    # before anything is written. A hit refuses the WHOLE compile:
    # no commit, the stamp unmoved, and the pings composed this
    # run never dispatch (they exist only in memory — the courier
    # reads the committed ledger at HEAD). The next tick
    # re-compiles the same interval once the source line is fixed.
    hits = scan_composed(rendered, ledger_new)
    if hits:
        write_refusal_alert(flagged=[{"file": p, "pattern": n}
                                     for p, n in hits])
        detail = "; ".join(f"{p} matches sweep pattern class {n}"
                           for p, n in hits)
        fail(f"secret-scan refusal: {detail} — commit refused, "
             f"stamp unmoved (the interval re-compiles next tick)")
    # compose -> write temp -> rename -> commit (the N3 invariant)
    tmpdir = os.path.join(gitdir, "board-compiler-tmp")
    os.makedirs(tmpdir, exist_ok=True)
    board_dir = os.path.join(repo.root, "memory", "board")
    os.makedirs(board_dir, exist_ok=True)
    tmp_board = os.path.join(tmpdir, "BOARD.md")
    tmp_ledger = os.path.join(tmpdir, "ping-ledger.jsonl")
    with open(tmp_board, "w") as fh:
        fh.write(rendered)
    with open(tmp_ledger, "w") as fh:
        fh.write(ledger_new)
    os.replace(tmp_board, os.path.join(board_dir, "BOARD.md"))
    os.replace(tmp_ledger, os.path.join(board_dir, "ping-ledger.jsonl"))
    crash_point("dispatch")
    if os.environ.get("BOARD_COMPILER_SIM_SWEEP_AFTER_RENAME"):
        # Test-only (stage 4 battery): simulate the whole-tree sweep
        # landing the renamed files first, so the writer's
        # empty-commit tolerance (N3(i)) is exercised in-run.
        sim_env = {"GIT_AUTHOR_NAME": "Mica",
                   "GIT_AUTHOR_EMAIL": "micaforge@gravicity.ai",
                   "GIT_COMMITTER_NAME": "Mica",
                   "GIT_COMMITTER_EMAIL": "micaforge@gravicity.ai"}
        repo.git("add", "--", BOARD_PATH, LEDGER_PATH, check=False)
        repo.git("commit", "-q", "-m", "memory: board files (sweep)",
                 check=False, env_extra=sim_env)
    env = {"GIT_AUTHOR_NAME": COMPILER_AUTHOR_NAME,
           "GIT_AUTHOR_EMAIL": COMPILER_AUTHOR_EMAIL,
           "GIT_COMMITTER_NAME": COMPILER_AUTHOR_NAME,
           "GIT_COMMITTER_EMAIL": COMPILER_AUTHOR_EMAIL}
    landed_by_sweep = False
    commit_sha = None
    for attempt in range(2):
        r = repo.git("add", "--", BOARD_PATH, LEDGER_PATH, check=False)
        staged = repo.git("diff", "--cached", "--quiet", "--",
                          BOARD_PATH, LEDGER_PATH, check=False)
        if staged.returncode == 0:
            # nothing staged: success iff HEAD already carries our
            # exact files (a sweep landed the rename — N3(i)).
            if repo.show(repo.head(), BOARD_PATH) == rendered and \
                    repo.show(repo.head(), LEDGER_PATH) == ledger_new:
                landed_by_sweep = True
                break
            fail("nothing staged and HEAD's board/ledger differ from "
                 "the rendered ones — refusing to claim the write")
        r = repo.git("commit", "-q", "-m",
                     f"{COMPILER_SUBJECT_PREFIX} compile through "
                     f"{head0[:12]}",
                     "-m", f"Compiled-Through: {head0}",
                     check=False, env_extra=env)
        if r.returncode == 0:
            commit_sha = repo.head()
            break
        if attempt == 0:
            time.sleep(2)
            continue
        fail(f"commit failed: {r.stderr.strip()[:240]}")
    # verified write: re-read the state the record itself shows
    rb = repo.show(repo.head(), BOARD_PATH)
    if board_stamp(rb) != head0:
        fail("read-back mismatch: HEAD's board stamp is "
             f"{board_stamp(rb)}, expected {head0}")
    clear_refusal_alert()
    pings = sum(1 for e in composed if e["kind"] == "ping")
    sup = sum(1 for e in composed if e["kind"] == "superseded")
    closes = sum(1 for e in composed if e["kind"] == "close")
    clears = sum(1 for e in composed if e["kind"] == "clear")
    pairs = sum(len(e["pairs"]) for e in v.entries.values())
    result = {"head": head0, "baseline": baseline,
              "rebaselined": rebaselined, "commits_walked": len(commits),
              "pings": pings, "superseded": sup, "closes": closes,
              "clears": clears, "c7_pairs": pairs,
              "lanes": len(v.entries),
              "coverage": f"{v.resolved_lines}/{v.total_lines}",
              "commit": commit_sha, "landed_by_sweep": landed_by_sweep,
              "scan": {"classes": len(load_sweep_patterns()),
                       "hits": 0},
              "verified_stamp": head0}
    if JSON_MODE:
        print(json.dumps(result))
    else:
        print(f"board: compiled "
              f"{(stamp or 'baseline')[:12]}..{head0[:12]}"
              f"{' (baseline)' if baseline else ''}"
              f"{' (REBASELINED — stamp not an ancestor)' if rebaselined else ''}")
        print(f"flips→pings {pings} · superseded {sup} · closes "
              f"{closes} · clears {clears} · C7 pairs {pairs}")
        print(f"lanes rendered {len(v.entries)} · coverage "
              f"{v.resolved_lines}/{v.total_lines} lines resolved")
        if landed_by_sweep:
            print("commit: landed by the sweep's commit — HEAD copy "
                  "verified identical")
        else:
            print(f"commit: {commit_sha[:12] if commit_sha else '—'} "
                  f"(board paths only; never pushed)")
        print(f"read-back: HEAD board stamp = {head0[:12]} ✓")
    return 0


def do_render(repo, records, out_path):
    head0 = repo.head()
    v = build_view(repo, head0, records)
    new_snapshot = {}
    for slug, entry in v.entries.items():
        if entry["band"] and entry["note"] in ("ok", "followed"):
            _, snap = dependency_flips(records, entry["lane"],
                                       entry["band"], v.prev_snapshot,
                                       None)
            new_snapshot.update(snap)
    if v.prev_stamp and v.prev_stamp != head0 and \
            repo.is_ancestor(v.prev_stamp, head0):
        _, commits = walk_flips(repo, v.prev_stamp, head0, v.included,
                                v.tree)
        touched = sweep_touched_lanes(commits, v.included)
    elif v.prev_stamp == head0:
        touched = "none (no pending interval)"
    else:
        touched = "baseline"
    text = render_board(v, head0, new_snapshot, touched, now_iso())
    if JSON_MODE:
        print(json.dumps({"head": head0, "lanes": len(v.entries),
                          "c7_pairs": sum(len(e["pairs"])
                                          for e in v.entries.values()),
                          "board": text}))
    elif out_path:
        with open(out_path, "w") as fh:
            fh.write(text)
        print(f"board: rendered at {head0[:12]} → {out_path} "
              f"(read-only; nothing committed)", file=sys.stderr)
    else:
        print(text)
    return 0


def do_check(repo, records, only_slug=None, more=False):
    head0 = repo.head()
    v = build_view(repo, head0, records)
    rows, total_pairs = [], 0
    for slug in sorted(v.entries):
        if only_slug and slug != only_slug:
            continue
        e = v.entries[slug]
        total_pairs += len(e["pairs"])
        rows.append({"lane": slug, "note": e["note"],
                     "schema": e["band"].state if e["band"] else None,
                     "pairs": [{"line": p["line"],
                                "evidence": p["evidence"]}
                               for p in e["pairs"]],
                     "c2": bool(e["c2"]),
                     "unresolvable": len(e["unresolvable"])})
    bad = [r for r in rows if r["pairs"]]
    if JSON_MODE:
        print(json.dumps({"head": head0, "lanes": rows,
                          "c7_pairs": total_pairs}))
    else:
        print(f"check @ {head0[:12]}: {len(rows)} lanes · "
              f"{total_pairs} C7 pair(s) · "
              f"{sum(1 for r in rows if r['c2'])} C2 prompt(s) · "
              f"{sum(r['unresolvable'] for r in rows)} unresolvable "
              f"assignment(s)")
        show = rows if more else bad
        for r in show[:10 if not more else 10000]:
            if r["pairs"] or more:
                print(f"- {r['lane']} (schema {r['schema']}, "
                      f"{r['note']}): {len(r['pairs'])} pair(s)")
                for p in r["pairs"]:
                    print(f"    ⚠ {p['line'][:110]} ↔ {p['evidence']}")
    return 1 if total_pairs else 0


def main(argv):
    global JSON_MODE
    args = argv[1:]
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0
    mode = "render"
    repo_root, ws_root, desks_arg = HOME, None, None
    out_path, only_slug, more = None, None, False
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
        elif a == "--lane":
            i += 1
            only_slug = args[i]
        elif a == "--file":
            i += 1
            only_slug = None
            mode = "check"
            # resolve the file's lane after the view exists: stash
            out_path = out_path or None
            main_file = args[i]
            globals()["_CHECK_FILE"] = main_file
        else:
            print(__doc__, file=sys.stderr)
            return 2
        i += 1
    repo = Repo(os.path.expanduser(repo_root))
    if not os.path.isdir(os.path.join(repo.root, ".git")) and \
            repo.git("rev-parse", "--git-dir", check=False).returncode:
        fail(f"{repo_root} is not a git repository")
    ws = ws_root or os.path.join(repo.root, "workspace")
    desk_roots = [desks_arg] if desks_arg else \
        [os.path.join(HOME, "skills"), "/opt/muse/skills"]
    records = Records(ws, desk_roots, home=repo.root)
    if mode == "write":
        return do_write(repo, records)
    if mode == "check":
        check_file = globals().get("_CHECK_FILE")
        if check_file and not only_slug:
            head0 = repo.head()
            lanes, included = resolve_inclusion(repo, head0)
            rel = os.path.relpath(os.path.expanduser(check_file),
                                  repo.root)
            for slug, lane in lanes.items():
                if rel in lane.band_candidates:
                    if lane.excluded:
                        print(f"check: {rel} is held by lane {slug}, "
                              f"excluded by its own marking — no "
                              f"content read")
                        return 0
                    only_slug = slug
                    break
        return do_check(repo, records, only_slug, more)
    return do_render(repo, records, out_path)


if __name__ == "__main__":
    # die quietly on a closed pipe (mica lane board | head) instead of
    # a BrokenPipeError traceback — standard SIGPIPE disposition.
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    sys.exit(main(sys.argv))
