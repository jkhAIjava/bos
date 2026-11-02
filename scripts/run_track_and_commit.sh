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

shopt -s nullglob
xlsx_files=(data/159941/*.xlsx)
if [[ ${#xlsx_files[@]} -eq 0 ]]; then
  echo "nothing to commit (no xlsx)"
  exit 0
fi
git add "${xlsx_files[@]}"
if [[ -z "$(git diff --cached --name-only -- data/159941/)" ]]; then
  echo "nothing to commit"
  exit 0
fi
git config user.email "cursor-automation@users.noreply.github.com"
git config user.name "Cursor Automation"
git commit -m "chore(159941): hourly quote $(TZ=Asia/Shanghai date +%Y-%m-%d\ %H:%M)" -- "${xlsx_files[@]}"
git push origin HEAD
