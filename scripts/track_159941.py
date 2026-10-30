#!/usr/bin/env python3
"""Fetch sz159941 (纳指ETF) quote and append to daily Excel under data/159941/."""

from __future__ import annotations

import re
import sys
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from chinese_calendar import is_workday
from openpyxl import Workbook, load_workbook

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "159941"
QUOTE_URL = "http://qt.gtimg.cn/q=sz159941"
CODE = "159941"
NAME = "纳指ETF"
TZ = ZoneInfo("Asia/Shanghai")

HEADERS = [
    "记录时间",
    "代码",
    "名称",
    "现价",
    "昨收",
    "涨跌额",
    "涨跌幅(%)",
    "行情时间",
]

MORNING = (time(9, 30), time(11, 30))
AFTERNOON = (time(13, 0), time(15, 0))


def in_trading_session(now: datetime) -> bool:
    if not is_workday(now.date()):
        return False
    t = now.time()
    return (MORNING[0] <= t <= MORNING[1]) or (AFTERNOON[0] <= t <= AFTERNOON[1])


def fetch_quote() -> dict[str, str | float]:
    resp = requests.get(QUOTE_URL, timeout=15)
    resp.encoding = "gbk"
    text = resp.text.strip()
    m = re.search(r'="([^"]+)"', text)
    if not m:
        raise RuntimeError(f"Unexpected quote response: {text[:200]}")
    parts = m.group(1).split("~")
    if len(parts) < 34:
        raise RuntimeError(f"Too few fields in quote: {len(parts)}")

    def f(idx: int) -> float:
        return float(parts[idx])

    return {
        "name": parts[1] or NAME,
        "code": parts[2] or CODE,
        "price": f(3),
        "prev_close": f(4),
        "change": f(31),
        "change_pct": f(32),
        "quote_time": parts[30] if len(parts) > 30 else "",
    }


def hour_key(record_time: str) -> str:
    """Same calendar hour upserts one row."""
    dt = datetime.fromisoformat(record_time)
    return dt.strftime("%Y-%m-%d %H")


def read_existing_rows(path: Path) -> list[list]:
    wb = load_workbook(path, read_only=True)
    ws = wb.active
    rows = [list(r) for r in ws.iter_rows(min_row=2, values_only=True)]
    wb.close()
    return rows


def write_workbook(path: Path, rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "159941"
    ws.append(HEADERS)
    for row in rows:
        ws.append(row)
    wb.save(path)


def append_or_upsert(path: Path, row: list, record_time: str) -> None:
    key = hour_key(record_time)
    if path.exists():
        existing = read_existing_rows(path)
        kept: list[list] = []
        replaced = False
        for old in existing:
            if not old or not old[0]:
                continue
            if hour_key(str(old[0])) == key:
                kept.append(row)
                replaced = True
            else:
                kept.append(old)
        if not replaced:
            kept.append(row)
        write_workbook(path, kept)
    else:
        write_workbook(path, [row])


def main() -> int:
    now = datetime.now(TZ)
    if not in_trading_session(now):
        print(f"Outside trading session ({now.isoformat()}), skip.")
        return 0

    q = fetch_quote()
    record_time = now.replace(second=0, microsecond=0).isoformat(timespec="seconds")
    day_file = DATA_DIR / f"{now.date().isoformat()}.xlsx"
    row = [
        record_time,
        q["code"],
        q["name"],
        q["price"],
        q["prev_close"],
        q["change"],
        q["change_pct"],
        q["quote_time"],
    ]
    append_or_upsert(day_file, row, record_time)
    print(f"Wrote {day_file} row at {record_time}, change_pct={q['change_pct']}%")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
