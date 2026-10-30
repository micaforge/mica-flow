#!/usr/bin/env bash
# mica flow close <flow> [--verify] [--yes] [--cycle <name>] [--json]
# Flow level: four phases: 1 VERIFY (V1–V5, read-only) · 2 HARVEST
# (reflect --flow) · 3 UPDATE (changelog + AGENT.md status; goal completion
# stays manual) · 4 ARCHIVE (nothing — D11 nudges later).
# Cycle level (--cycle): per-wave close gate (C1–C5, read-only). Run after
# every wave; the next wave must not dispatch until this passes.
# --verify: run Phase 1 only. Exit 1 on BLOCKED.
set -uo pipefail
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  sed -n '2,8p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 0
fi
source ~/workspace/caps/_shared/output.sh
eval "$(mica_parse_output_flags "$@")"

VERIFY_ONLY=0; YES=0; JSON=0; CYCLE=""; WANT_CYCLE=0
FLOW=""
for a in "${MICA_REMAINING[@]}"; do
  case "$a" in
    --verify) VERIFY_ONLY=1;; --yes) YES=1;; --json) JSON=1;;
    --cycle) WANT_CYCLE=1;;
    *) if [[ $WANT_CYCLE -eq 1 ]]; then CYCLE="$a"; WANT_CYCLE=0;
       elif [[ -z "$FLOW" ]]; then FLOW="$a"; fi;;
  esac
done
[[ -z "$FLOW" ]] && { echo "usage: mica flow close <flow> [--verify] [--yes] [--cycle <name>] [--json]" >&2; exit 1; }

FLOWS_DIR="${FLOWS_DIR:-$HOME/workspace/flows}"
FD="$FLOWS_DIR/$FLOW"
[[ -d "$FD" ]] || { echo "unknown flow: $FLOW" >&2; exit 1; }

FAIL=""

fail() { FAIL+="$1"$'\n'; }

verdict() { # $1 = subject label
  local subj="$1"
  if [[ -n "$FAIL" ]]; then
    if [[ $JSON -eq 1 ]]; then
      printf '{"flow":"%s","subject":"%s","verdict":"BLOCKED","failures":[' "$FLOW" "$subj"
      first=1
      while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        [[ $first -eq 0 ]] && printf ','
        printf '"%s"' "${f//\"/\\\"}"; first=0
      done <<< "$FAIL"
      echo ']}'
    else
      echo "BLOCKED: $subj"
      echo "$FAIL" | head -10
      n=$(echo "$FAIL" | grep -c .)
      [[ $n -gt 10 ]] && echo "... ($((n-10)) more)"
    fi
    exit 1
  fi
  if [[ $JSON -eq 1 ]]; then
    printf '{"flow":"%s","subject":"%s","verdict":"PASS"}\n' "$FLOW" "$subj"
  else
    echo "PASS: $subj"
  fi
  exit 0
}

# ============ CYCLE LEVEL: per-wave close gate (C1–C5) ============
if [[ -n "$CYCLE" ]]; then
  cdir=$(find "$FD" -maxdepth 3 -type d -name "$CYCLE" | head -1)
  [[ -n "$cdir" ]] || { echo "unknown cycle: $CYCLE (under $FLOW)" >&2; exit 1; }
  cn=$(basename "$cdir"); cm="$cdir/cycle.md"; bm="$cdir/BRIEF.md"; rundir="$cdir/_run"

  # --- C1: cycle status is done (accept legacy 'complete') ---
  st=$(grep -m1 '^status:' "$cm" 2>/dev/null | awk '{print $2}')
  [[ "$st" == "done" || "$st" == "complete" ]] || fail "C1: $cn status='$st' (want done)"

  # --- C2: _run/ exists and holds deliverables ---
  if [[ ! -d "$rundir" ]] || [[ -z "$(ls -A "$rundir" 2>/dev/null)" ]]; then
    fail "C2: $cn _run/ missing or empty"
  fi

  # --- C3: gates table — no bare TODO in gate/verify columns ---
  while IFS= read -r row; do
    gate=$(echo "$row" | awk -F'|' '{print $3}')
    vercol=$(echo "$row" | awk -F'|' '{print $4}')
    if grep -qE '^\s*TODO\s*$' <<< "$gate" || grep -qE '^\s*TODO\s*$' <<< "$vercol"; then
      fail "C3: $cn has bare TODO gate (fix cycle.md)"
    fi
  done < <(grep -E '^\| *G[0-9]+' "$cm" 2>/dev/null || true)

  # --- C4: brief deliverables all present in _run/ ---
  if [[ -f "$bm" ]]; then
    in_deliv=0
    while IFS= read -r line; do
      [[ "$line" =~ ^##[[:space:]]+Deliverables ]] && { in_deliv=1; continue; }
      [[ "$line" =~ ^##[[:space:]] ]] && in_deliv=0
      [[ $in_deliv -eq 0 ]] && continue
      # only item-head lines; description after the first em-dash may name
      # files that are subjects, not deliverables
      [[ "$line" =~ ^([0-9]+\.|[[:space:]]*[-*])[[:space:]] ]] || continue
      item="${line%%—*}"
      while IFS= read -r fn; do
        [[ -z "$fn" ]] && continue
        nfn="${fn#../}"  # brief may path the next brief relative to the cycle dir, not _run/
        [[ "$nfn" =~ ^a[0-9][0-9]-.*/BRIEF\.md$ ]] && continue  # C5 handles next-brief
        shopt -s nullglob; _m=("$rundir"/$fn); shopt -u nullglob
        [[ ${#_m[@]} -gt 0 ]] || fail "C4: $cn deliverable missing from _run/: $fn"
      done < <(grep -o '`[^`]*`' <<< "$item" | tr -d '`')
    done < "$bm"
  else
    fail "C4: $cn missing BRIEF.md"
  fi

  # --- C5: next cycle's BRIEF exists, ready, no TODOs (unless final) ---
  if [[ "$cn" =~ ^a([0-9]+)- ]]; then
    next_n=$(printf 'a%02d' $((10#${BASH_REMATCH[1]} + 1)))
    ndir=$(find "$FD" -maxdepth 3 -type d -name "${next_n}-*" | head -1)
    if [[ -n "$ndir" ]]; then
      nbm="$ndir/BRIEF.md"
      [[ -f "$nbm" ]] || fail "C5: next cycle $(basename "$ndir") missing BRIEF.md"
      if [[ -f "$nbm" ]]; then
        nst=$(grep -m1 '^status:' "$nbm" | awk '{print $2}')
        [[ "$nst" == "ready" ]] || fail "C5: next brief status='$nst' (want ready)"
        hits=$(grep -nE '^\s*TODO\b|TODO:' "$nbm" | head -3)
        [[ -n "$hits" ]] && fail "C5: next brief has TODOs: $hits"
      fi
    fi
    # no successor dir → final cycle: C5 vacuously passes
  fi

  verdict "$FLOW/$cn"
fi

# --- V1: every cycle status: done ---
declare -a CYCLES=()
while IFS= read -r cm; do
  CYCLES+=("$cm")
  st=$(grep -m1 '^status:' "$cm" | awk '{print $2}')
  [[ "$st" == "done" ]] || fail "V1: $(dirname "$cm" | xargs basename) status='$st' (want done)"
done < <(find "$FD" -maxdepth 3 -name cycle.md | sort)
[[ ${#CYCLES[@]} -eq 0 ]] && fail "V1: no cycle.md found"

# --- V2: gates table — bare TODO in gate (col 2) or verify (col 3) columns only ---
for cm in "${CYCLES[@]}"; do
  cdir=$(dirname "$cm"); cn=$(basename "$cdir")
  while IFS= read -r row; do
    # split on |, cols: 1=# 2=gate 3=verify 4=pass
    gate=$(echo "$row" | awk -F'|' '{print $3}')
    vercol=$(echo "$row" | awk -F'|' '{print $4}')
    if grep -qE '^\s*TODO\s*$' <<< "$gate" || grep -qE '^\s*TODO\s*$' <<< "$vercol"; then
      fail "V2: $cn has bare TODO gate (fix cycle.md)"
    fi
  done < <(grep -E '^\| *G[0-9]+' "$cm" 2>/dev/null || true)
done

# --- V3: ready briefs have 0 standalone TODOs ---
while IFS= read -r bm; do
  st=$(grep -m1 '^status:' "$bm" | awk '{print $2}')
  [[ "$st" == "ready" ]] || continue
  hits=$(grep -nE '^\s*TODO\b|TODO:' "$bm" | head -3)
  [[ -n "$hits" ]] && fail "V3: $bm has TODOs: $hits"
done < <(find "$FD" -maxdepth 3 -name BRIEF.md | sort)

# --- V4: done cycles' _run/ matches brief deliverables (next-BRIEF excluded) ---
for cm in "${CYCLES[@]}"; do
  st=$(grep -m1 '^status:' "$cm" | awk '{print $2}')
  [[ "$st" == "done" ]] || continue
  cdir=$(dirname "$cm"); cn=$(basename "$cdir")
  bm="$cdir/BRIEF.md"; rundir="$cdir/_run"
  [[ -f "$bm" ]] || { fail "V4: $cn missing BRIEF.md"; continue; }
  in_deliv=0
  while IFS= read -r line; do
    [[ "$line" =~ ^##[[:space:]]+Deliverables ]] && { in_deliv=1; continue; }
    [[ "$line" =~ ^##[[:space:]] ]] && in_deliv=0
    [[ $in_deliv -eq 0 ]] && continue
    [[ "$line" =~ ^([0-9]+\.|[[:space:]]*[-*])[[:space:]] ]] || continue
    item="${line%%—*}"
    while IFS= read -r fn; do
      [[ -z "$fn" ]] && continue
      nfn="${fn#../}"  # brief may path the next brief relative to the cycle dir, not _run/
      if [[ "$nfn" =~ ^a[0-9][0-9]-.*/BRIEF\.md$ ]]; then
        nbn="${nfn%%/*}"
        nc=$(find "$FD" -maxdepth 3 -type d -name "$nbn" | head -1)
        { [[ -n "$nc" && -f "$nc/BRIEF.md" ]]; } || fail "V4: $cn next brief missing: $fn"
      else
        shopt -s nullglob; _m=("$rundir"/$fn); shopt -u nullglob
        [[ ${#_m[@]} -gt 0 ]] || fail "V4: $cn deliverable missing from _run/: $fn"
      fi
    done < <(grep -o '`[^`]*`' <<< "$item" | tr -d '`')
  done < "$bm"
done

# --- V5: final cycle wrote no "next BRIEF" ---
last_cm=$(printf '%s\n' "${CYCLES[@]}" | sort | tail -1)
if [[ -n "$last_cm" ]]; then
  ldir=$(dirname "$last_cm"); lbm="$ldir/BRIEF.md"
  if [[ -f "$lbm" ]] && grep -qE 'a[0-9][0-9]-.*/BRIEF\.md|next BRIEF' "$lbm"; then
    fail "V5: final cycle references a next BRIEF (flow not actually last)"
  fi
  # no aNN+1 dir beyond the last
  last_n=$(basename "$ldir" | grep -oE '^a[0-9]+' | grep -oE '[0-9]+')
  if [[ -n "$last_n" ]]; then
    next_n=$(printf 'a%02d' $((10#$last_n + 1)))
    if find "$FD" -maxdepth 3 -type d -name "${next_n}-*" | grep -q .; then
      fail "V5: $next_n-* dir exists beyond final cycle"
    fi
  fi
fi

# --- verdict (flow level) ---
if [[ -n "$FAIL" ]]; then
  if [[ $JSON -eq 1 ]]; then
    printf '{"flow":"%s","verdict":"BLOCKED","failures":[' "$FLOW"
    first=1
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      [[ $first -eq 0 ]] && printf ','
      printf '"%s"' "${f//\"/\\\"}"; first=0
    done <<< "$FAIL"
    echo ']}'
  else
    echo "BLOCKED: $FLOW"
    echo "$FAIL" | head -10
    n=$(echo "$FAIL" | grep -c .)
    [[ $n -gt 10 ]] && echo "... ($((n-10)) more)"
  fi
  exit 1
fi

echo "CLOSE-READY: $FLOW (${#CYCLES[@]} cycles, V1–V5 pass)"
[[ $VERIFY_ONLY -eq 1 ]] && exit 0

# --- Phase 2 HARVEST ---
echo "--- phase 2: harvest ---"
echo "Preview (dry-run):"
~/workspace/bin/mica context reflect --flow "$FLOW" --dry-run 2>&1 | head -40
if [[ $YES -eq 0 ]]; then
  read -rp "Write this MLR block to today's memory file? [y/N] " ans
  [[ "$ans" =~ ^[Yy]$ ]] || { echo "harvest skipped"; exit 0; }
fi
~/workspace/bin/mica context reflect --flow "$FLOW" 2>&1 | head -12

# --- Phase 3 UPDATE ---
echo "--- phase 3: update ---"
# changelog
TS=$(date +%F)
echo "$TS — flow '$FLOW' closed: ${#CYCLES[@]} cycles, V1–V5 verified, MLR harvested." >> "$HOME/CHANGELOG.md"
echo "  changelog: appended to ~/CHANGELOG.md"
# AGENT.md status: seeded → complete
AGENT="$FD/AGENT.md"
if [[ -f "$AGENT" ]]; then
  if grep -q '^status: seeded' "$AGENT"; then
    sed -i 's/^status: seeded/status: complete/' "$AGENT"
    echo "  AGENT.md: status seeded → complete"
  else
    echo "  AGENT.md: no 'status: seeded' to flip (manual check)"
  fi
else
  echo "  AGENT.md: not found (skip)"
fi
# goal completion stays approval-gated
echo "  goal: NOT auto-completed — run manually when Curtis approves:"
echo "    user_goal set_status completed (goal id from ~/workspace/goals/)"

# --- Phase 4 ARCHIVE ---
echo "--- phase 4: archive ---"
echo "  nothing to do (dir stays; D11 nudges archival after 30d idle)"
echo "CLOSED: $FLOW"
exit 0
