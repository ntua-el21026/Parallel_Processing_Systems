#!/usr/bin/env bash
# Copy the CONTENTS of a local directory from ORION to your home on SCIRouter.
# Usage:
#   ~/push_to_scirouter.sh <source_dir> [destination_name]
# Example:
#   ~/push_to_scirouter.sh ~/a2
#   ~/push_to_scirouter.sh ~/a2 lab_a2_backup

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $(basename "$0") <source_dir> [destination_name]" >&2
  exit 1
fi

SRC_INPUT="$1"
DEST_NAME="${2:-$(basename "$SRC_INPUT")}"

# Resolve absolute path
if ! SRC_ABS="$(readlink -f -- "$SRC_INPUT" 2>/dev/null)"; then
  pushd "$(dirname "$SRC_INPUT")" >/dev/null
  SRC_ABS="$(pwd -P)/$(basename "$SRC_INPUT")"
  popd >/dev/null
fi

if [[ ! -d "$SRC_ABS" ]]; then
  echo "Error: directory not found: $SRC_ABS" >&2
  exit 1
fi

# Ensure destination dir exists on scirouter
ssh scirouter "mkdir -p ~/'$DEST_NAME'"

echo "Copying contents of $SRC_ABS  →  scirouter:~/$DEST_NAME/ ..."
scp -Crp "$SRC_ABS"/. "scirouter:~/$DEST_NAME/"
echo "Done."
