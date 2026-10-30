#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m pip install -q -r scripts/requirements-track.txt
python3 scripts/track_159941.py

if git status --porcelain -- data/159941/ | grep -q .; then
  git config user.email "352531148@qq.com"
  git config user.name "jinx"
  git add data/159941/
  git commit -m "chore(159941): update intraday quote $(TZ=Asia/Shanghai date +%Y-%m-%d\ %H:%M)"
  git push origin HEAD
fi
