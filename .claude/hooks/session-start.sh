#!/bin/bash
# Cloud session start (claude.ai/code), 5.10: the repo's main up to date and the Python packages the tools and
# the agent need -- pillow (reading screenshots of runs), openpyxl (regen_vc_tgr.py / regen_hc_vc.py: ideology
# stances), vic3tools (the parser behind ld_pdx.py / vic3lib.py and the v3 command; from the sibling checkout if
# there is one, else from GitHub). Local and Remote Control sessions run on the user's PC and do not use this hook.
# The vic3tools plugin (skills, hooks) cannot be enabled from here or from .claude/settings.json in the cloud: the
# environment's setup script installs it -- vic3_tools/claude-plugin/cloud-setup.sh, its README "Cloud sessions".
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
if [ -d "$CLAUDE_PROJECT_DIR/../vic3_tools" ]; then
  VIC3TOOLS="-e $CLAUDE_PROJECT_DIR/../vic3_tools"
else
  VIC3TOOLS="git+https://github.com/BEDTRIP/vic3_tools@main"
fi
python3 -m pip install --quiet --disable-pip-version-check $VIC3TOOLS 2>&1 | grep -v "WARNING: Running pip as the 'root' user" || true
