#!/usr/bin/env bash
# Usage: tools/launch.sh "<pipeline args>" [kernel-slug]   (pins the current pushed HEAD)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
COMMIT=$(git -C "$ROOT" rev-parse HEAD)
TMP=$(mktemp -d)
SLUG=${2:-wn-run}
sed "s|__SLUG__|$SLUG|g" "$ROOT/kaggle/run/kernel-metadata.json" > "$TMP/kernel-metadata.json"
sed -e "s|__COMMIT__|$COMMIT|" -e "s|__ARGS__|$1|" "$ROOT/kaggle/run/run.py" > "$TMP/run.py"
cd /tmp && KAGGLE_USERNAME=shreysharma07 python "$ROOT/tools/kaggle_cli.py" kernels push -p "$TMP" 2>&1 | tail -1
