#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m pip install -q -r "$ROOT/scripts/requirements-track.txt"

python3 "$ROOT/scripts/track_159941.py"
status=$?
if [[ "$status" -ne 0 ]]; then
  exit "$status"
fi

if [[ -z "$(git status --porcelain -- data/159941/)" ]]; then
  echo "no changes under data/159941/"
  exit 0
fi

git add -- data/159941/
if git diff --cached --quiet -- data/159941/; then
  echo "no staged changes under data/159941/"
  exit 0
fi

git config user.email "cursor-automation@users.noreply.github.com"
git config user.name "Cursor Automation"
git commit -m "chore(159941): hourly quote $(TZ=Asia/Shanghai date +%Y-%m-%d\ %H:%M)" -- data/159941/
git push origin HEAD
