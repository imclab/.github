#!/bin/zsh
# Daily refresh of the 3D contribution calendar, run by launchd (scripts/com.imclab.contrib3d.plist), no GitHub Actions.
set -euo pipefail
cd "${0:A:h}/.."
git pull -q --rebase
python3 scripts/contrib3d.py JT5D profile-3d-contrib
git add profile-3d-contrib
git diff --cached --quiet || git commit -qm "3D contribution calendar $(date +%F)"
git push -q
echo "$(date '+%F %T') refreshed $(git rev-parse --short HEAD)"
