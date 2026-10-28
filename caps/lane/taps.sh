#!/usr/bin/env bash
# mica lane taps [--more] [--all] [--json] [--limit N]
# Unified pending-decision view. Reads tap files from
# ~/workspace/flows/<parent>/taps/<tap-id>.md (frontmatter + brief body).
# Falls back to LANES.md "Human taps" cells for parents without tap files.
#
# Output contract:
#   default : one line per open tap (parent · lane — summary)
#   --more  : full brief per tap (spec format)
#   --all   : include decided/superseded taps
#   --json  : machine-readable, all frontmatter fields + body
set -uo pipefail
source ~/workspace/caps/_shared/output.sh
eval "$(mica_parse_output_flags "$@")"

JSON=0; ALL=0
# NOTE: mica_parse_output_flags consumes --all as an alias of --more (shared
# helper), so it never reaches MICA_REMAINING. Scan the raw args here:
# in taps.sh --all has its own meaning (include decided/superseded taps),
# distinct from --more (full briefs). The two flags stay orthogonal.
for a in "$@"; do
  [[ "$a" == "--all" ]] && ALL=1
done
for a in "${MICA_REMAINING[@]}"; do
  [[ "$a" == "--json" ]] && JSON=1
done

FLOWS_DIR="${FLOWS_DIR:-$HOME/workspace/flows}"

# Parse frontmatter field from a tap file
tap_field() {
  local file="$1" key="$2"
  awk -v k="$key" '
    /^---$/ { if (++n == 2) exit; next }
    n == 1 && $0 ~ "^" k ":" {
      sub("^" k ":[[:space:]]*", ""); print; exit
    }
  ' "$file"
}

# Extract body (everything after second ---)
tap_body() {
  awk 'BEGIN{n=0} /^---$/ {n++; next} n>=2 {print}' "$1"
}

# One-line summary: first **Decision:** line, or id
tap_summary() {
  local body summary
  body="$(tap_body "$1")"
  summary="$(printf '%s' "$body" | grep -m1 '^\*\*Decision:' | sed 's/^\*\*Decision:[[:space:]]*//;s/\*\*$//')"
  [[ -z "$summary" ]] && summary="$(tap_field "$1" id)"
  printf '%s' "$summary"
}

# Collect tap files
declare -a tap_files=()
while IFS= read -r f; do
  tap_files+=("$f")
done < <(find "$FLOWS_DIR" -path "*/taps/*.md" 2>/dev/null | sort)

# Filter by status (unless --all)
declare -a open_taps=()
for f in "${tap_files[@]}"; do
  status="$(tap_field "$f" id >/dev/null; tap_field "$f" status)"
  [[ -z "$status" ]] && status="open"
  if [[ "$ALL" -eq 1 ]] || [[ "$status" == "open" ]]; then
    open_taps+=("$f")
  fi
done

if [[ $JSON -eq 1 ]]; then
  python3 - "$FLOWS_DIR" "${open_taps[@]}" <<'PYEOF'
import sys, json, re

def parse_tap(path):
    with open(path) as fh:
        text = fh.read()
    # Split frontmatter
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
    if not m:
        return {"file": path, "error": "no frontmatter"}
    fm_text, body = m.group(1), m.group(2)
    fm = {}
    premises = []
    in_premises = False
    for line in fm_text.split('\n'):
        if re.match(r'^premises:\s*$', line):
            in_premises = True
            continue
        if in_premises and re.match(r'^\s+-\s+', line):
            premises.append(re.sub(r'^\s+-\s+', '', line).strip())
            continue
        in_premises = False
        kv = re.match(r'^([a-z_]+):\s*(.*)$', line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip()
    fm['premises'] = premises
    fm['body'] = body.strip()
    fm['file'] = path
    return fm

taps = [parse_tap(f) for f in sys.argv[2:]]
print(json.dumps(taps, indent=2))
PYEOF
  exit 0
fi

if [[ ${#open_taps[@]} -eq 0 ]]; then
  echo "no pending taps"
  exit 0
fi

if [[ "$MICA_MORE" == "1" ]]; then
  # Full brief per tap
  first=1
  for f in "${open_taps[@]}"; do
    [[ $first -eq 0 ]] && echo "---"
    parent="$(tap_field "$f" parent)"
    lane="$(tap_field "$f" lane)"
    echo "[$parent · $lane]"
    tap_body "$f"
    first=0
  done
else
  # One line per tap
  for f in "${open_taps[@]}"; do
    parent="$(tap_field "$f" parent)"
    lane="$(tap_field "$f" lane)"
    summary="$(tap_summary "$f")"
    echo "$parent · $lane — $summary"
  done | mica_truncate
fi
