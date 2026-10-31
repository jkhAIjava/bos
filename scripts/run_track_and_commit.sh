#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m pip install -q -r requirements.txt
python3 scripts/track_159941.py
status=$?
if [[ $status -ne 0 ]]; then
  exit "$status"
fi

xlsx_changes="$(git status --porcelain -- "data/159941/" | grep -E '\.xlsx$' || true)"
if [[ -z "$xlsx_changes" ]]; then
  echo "无 Excel 变更，跳过提交"
  exit 0
fi

git add -- data/159941/*.xlsx 2>/dev/null || true
if git diff --cached --quiet -- "data/159941/"; then
  echo "无 staged Excel 变更"
  exit 0
fi

git config user.email "cursor-automation@users.noreply.github.com"
git config user.name "Cursor Automation"
git commit -m "data(159941): 更新 $(TZ=Asia/Shanghai date +%Y-%m-%d) 纳指100 ETF  hourly 行情" -- data/159941/
git push origin HEAD
