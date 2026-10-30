#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 -m pip install -q -r requirements-track.txt

if ! python3 scripts/track_159941.py; then
  exit 1
fi

if ! git diff --quiet -- data/159941/ 2>/dev/null || [[ -n "$(git status --porcelain data/159941/ 2>/dev/null)" ]]; then
  git add data/159941/
  if git diff --cached --quiet; then
    exit 0
  fi
  DATE="$(TZ=Asia/Shanghai date +%Y-%m-%d\ %H:%M)"
  git commit -m "chore(159941): update intraday snapshot ${DATE}"
  git push origin HEAD
fi
