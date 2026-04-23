#!/bin/bash
# Download GAMSLIB raw `.gms` sources into `data/gamslib/raw/` for CI.
#
# For each model selected by mode, fetch the model's HTML landing page and
# extract the real download URL from the "Main file" link (the seq number in
# `gamslib_status.json::source_url` does NOT match the download URL — the
# status JSON field is stale/wrong, so we scrape the live page instead).
#
# Usage:
#   ./scripts/download_gamslib_raw.sh              # Convex in-scope models (nightly)
#   ./scripts/download_gamslib_raw.sh --fast       # 5 TestDeterminismFast fixtures
#   ./scripts/download_gamslib_raw.sh --all        # Every model in the status JSON
#   ./scripts/download_gamslib_raw.sh --help

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATUS_JSON="${REPO_ROOT}/data/gamslib/gamslib_status.json"
TARGET_DIR="${REPO_ROOT}/data/gamslib/raw"
BASE_URL="https://www.gams.com/latest/gamslib_ml"

MODE="convex"

# Fast-suite fixtures — loaded from the shared manifest file so the shell
# script and Python test can't drift out of sync. One model_id per line;
# blanks and `#` comments are ignored.
FAST_FIXTURES_MANIFEST="${REPO_ROOT}/tests/integration/determinism_fast_fixtures.txt"

show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Download GAMSLIB raw .gms sources into data/gamslib/raw/.

OPTIONS:
    --help          Show this help message
    --all           Download every model in the status JSON
    --fast          Download only the fixtures listed in
                    tests/integration/determinism_fast_fixtures.txt
                    (the same list TestDeterminismFast parametrizes over)

Default: convex in-scope models (likely_convex + verified_convex) that are
not skipped by pipeline_status and have nlp2mcp_translate.status == success;
this is the set targeted by TestDeterminismFull.
EOF
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --help) show_help; exit 0 ;;
        --all)  MODE="all"; shift ;;
        --fast) MODE="fast"; shift ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if [ ! -f "$STATUS_JSON" ]; then
    echo "ERROR: status JSON not found at $STATUS_JSON" >&2
    exit 1
fi

mkdir -p "$TARGET_DIR"

# Select model_ids by mode. For --fast mode, load fixtures from the shared
# manifest file so the shell script and the Python test read from the same
# source of truth.
if [ "$MODE" = "fast" ]; then
    if [ ! -f "$FAST_FIXTURES_MANIFEST" ]; then
        echo "ERROR: fast-fixture manifest not found at $FAST_FIXTURES_MANIFEST" >&2
        exit 1
    fi
    FAST_LIST="$(grep -v '^#' "$FAST_FIXTURES_MANIFEST" | tr '\n' ' ')"
else
    FAST_LIST=""
fi
MODEL_IDS="$(FAST_LIST="$FAST_LIST" python3 - "$STATUS_JSON" "$MODE" <<'PYEOF'
import json, os, sys
status_path, mode = sys.argv[1], sys.argv[2]
fast_set = set(os.environ.get("FAST_LIST", "").split())
data = json.loads(open(status_path).read())
for e in data["models"]:
    if mode == "convex":
        # Must match TestDeterminismFull._convex_models(): convex AND not
        # explicitly skipped AND baseline translate succeeded. Downloading
        # additional models would just waste the runner's bandwidth since
        # they'd be filtered out of the sweep anyway.
        if (e.get("convexity") or {}).get("status") not in (
            "likely_convex", "verified_convex",
        ):
            continue
        if (e.get("pipeline_status") or {}).get("status") == "skipped":
            continue
        if (e.get("nlp2mcp_translate") or {}).get("status") != "success":
            continue
    elif mode == "fast":
        if e["model_id"] not in fast_set:
            continue
    print(e["model_id"])
PYEOF
)"

if [ -z "$MODEL_IDS" ]; then
    echo "No models to download (mode=$MODE)" >&2
    exit 0
fi

TOTAL=$(echo "$MODEL_IDS" | wc -l | tr -d ' ')
echo "Downloading $TOTAL models (mode=$MODE) → $TARGET_DIR"

# Resolve the real download URL for a given model by scraping the model's
# landing page. Echoes "<url>" on success, empty on failure.
#
# The pipeline is wrapped in `|| true` so a `grep` no-match (exit 1) does not
# trip `set -e` — we want per-model failures to be reported and skipped, not
# to abort the entire download run.
resolve_url() {
    local name="$1"
    local url
    url="$(
        curl -fsS --max-time 15 --retry 2 \
            "${BASE_URL}/libhtml/gamslib_${name}.html" 2>/dev/null \
            | grep -oE 'Main file.*</p>' \
            | grep -oE 'href="[^"]+"' \
            | head -1 \
            | sed "s/^href=\"\.\.\///; s/\"$//; s|^|${BASE_URL}/|" \
            || true
    )"
    printf '%s\n' "$url"
    return 0
}

SUCCESS=0
SKIPPED=0
FAILED=0
while IFS= read -r name; do
    [ -z "$name" ] && continue
    target="${TARGET_DIR}/${name}.gms"

    if [ -s "$target" ]; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    url="$(resolve_url "$name")"
    if [ -z "$url" ]; then
        echo "FAILED: $name (could not resolve download URL)" >&2
        FAILED=$((FAILED + 1))
        continue
    fi

    if curl -fsS --retry 2 --max-time 30 -o "$target" "$url"; then
        SUCCESS=$((SUCCESS + 1))
    else
        echo "FAILED: $name ($url)" >&2
        rm -f "$target"
        FAILED=$((FAILED + 1))
    fi
done <<< "$MODEL_IDS"

echo "Summary: $SUCCESS downloaded, $SKIPPED already present, $FAILED failed (total $TOTAL)"
[ "$FAILED" -eq 0 ]
