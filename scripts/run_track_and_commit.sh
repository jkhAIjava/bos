#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

pip install -q -r scripts/requirements.txt
python3 scripts/track_159941.py "$@"

if [ -z "$(git status --porcelain -- data/159941/)" ]; then
  echo "No Excel changes to commit."
  exit 0
fi

git add data/159941/
git config user.name "cursor-automation"
git config user.email "cursor-automation@users.noreply.github.com"
DATE="$(TZ=Asia/Shanghai date +%F)"
git commit -m "data(159941): hourly quote snapshot ${DATE}"
git push origin HEAD
