#!/bin/bash
# Syncs data/processed and data/augmented from this Mac to Google Drive,
# to the exact path the Colab notebooks read from (BASE in RQ3_DANN.ipynb
# and 🧩LuckBasedModel(2).ipynb):
#   KachornLuckbasedThSL/KachornThSL/data/{processed,augmented}
#
# One-time setup: already done (2026-08-12). The rclone remote is named
# "drive" (not "gdrive" - rclone config landed on that name for this setup).
# Check anytime with: rclone listremotes
#
# To run the sync:
#   ./scripts/sync_to_drive.sh

set -e

REMOTE="drive"
DRIVE_PATH="KachornLuckbasedThSL/KachornThSL/data"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
LOCAL_DATA="$REPO_ROOT/data"

if ! command -v rclone &> /dev/null; then
  echo "rclone not installed. Run: brew install rclone"
  exit 1
fi

if ! rclone listremotes | grep -q "^${REMOTE}:$"; then
  echo "No rclone remote named '${REMOTE}' found."
  echo "Run 'rclone config' first - see the setup comment at the top of this script."
  exit 1
fi

echo "Syncing data/processed -> Drive:${DRIVE_PATH}/processed ..."
rclone sync "$LOCAL_DATA/processed" "${REMOTE}:${DRIVE_PATH}/processed" \
  --progress --checksum

echo "Syncing data/augmented -> Drive:${DRIVE_PATH}/augmented ..."
rclone sync "$LOCAL_DATA/augmented" "${REMOTE}:${DRIVE_PATH}/augmented" \
  --progress --checksum

echo "Done. Drive now matches this Mac's data/processed and data/augmented exactly."
