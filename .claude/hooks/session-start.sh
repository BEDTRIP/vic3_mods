#!/bin/bash
# Cloud session start (claude.ai/code), 5.10: the repo's main up to date and the Python packages the tools and
# the agent need -- pillow (reading screenshots of runs), openpyxl (regen_vc_tgr.py / regen_hc_vc.py: ideology
# stances). Local and Remote Control sessions run on the user's PC and do not use this hook.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
# one branch, main, for every mode (local, Remote Control, cloud) -- start from its latest state
if [ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] && [ -z "$(git status --porcelain)" ]; then
  git pull --ff-only --quiet origin main || echo "session-start: git pull failed (offline?) - going on"
fi
python3 -m pip install --quiet --disable-pip-version-check pillow openpyxl 2>&1 | grep -v "WARNING: Running pip as the 'root' user" || true
