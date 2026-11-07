#!/usr/bin/env bash
# Usage: tools/launch.sh "<pipeline args>" [kernel-slug] [source-kernel-slug]   (pins the current pushed HEAD)
# A source kernel's output is mounted under /kaggle/input; pass --seed-dir /kaggle/input to reuse it.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
COMMIT=$(git -C "$ROOT" rev-parse HEAD)
TMP=$(mktemp -d)
SLUG=${2:-wn-run}
SRC=${3:-}
SRCJSON=""
[ -n "$SRC" ] && SRCJSON="\"shreysharma07/$SRC\""
sed -e "s|__SLUG__|$SLUG|g" -e "s|__SOURCES__|$SRCJSON|" "$ROOT/kaggle/run/kernel-metadata.json" > "$TMP/kernel-metadata.json"
sed -e "s|__COMMIT__|$COMMIT|" -e "s|__ARGS__|$1|" "$ROOT/kaggle/run/run.py" > "$TMP/run.py"
cd /tmp && KAGGLE_USERNAME=shreysharma07 python "$ROOT/tools/kaggle_cli.py" kernels push -p "$TMP" 2>&1 | tail -1
