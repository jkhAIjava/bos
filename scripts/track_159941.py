#!/usr/bin/env python3
"""Fetch sz159941 (纳指ETF) quote and append a row to daily Excel under data/159941/."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

import requests
from openpyxl import Workbook, load_workbook

BEIJING = timezone(timedelta(hours=8))
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "159941"
TENCENT_URL = "https://qt.gtimg.cn/q=sz159941"

HEADERS = [
    "记录时间",
    "名称",
    "代码",
    "最新价",
    "昨收",
    "今开",
    "涨跌额",
    "涨跌幅(%)",
    "最高价",
    "最低价",
    "成交量(手)",
    "成交额(元)",
    "行情时间",
]

MORNING = (time(9, 30), time(11, 30))
AFTERNOON = (time(13, 0), time(15, 0))


def now_beijing() -> datetime:
    return datetime.now(BEIJING)


def in_trading_session(dt: datetime) -> bool:
    if dt.weekday() >= 5:
        return False
    t = dt.time()
    return (MORNING[0] <= t <= MORNING[1]) or (AFTERNOON[0] <= t <= AFTERNOON[1])


def parse_tencent(raw: str) -> dict[str, str]:
    m = re.search(r'v_sz159941="([^"]+)"', raw)
    if not m:
        raise ValueError("Unexpected Tencent response format")
    parts = m.group(1).split("~")
    if len(parts) < 34:
        raise ValueError(f"Too few fields in quote: {len(parts)}")

    def g(i: int) -> str:
        return parts[i] if i < len(parts) else ""

    quote_time = g(30)
    if len(quote_time) == 14:
        quote_time = (
            f"{quote_time[0:4]}-{quote_time[4:6]}-{quote_time[6:8]} "
            f"{quote_time[8:10]}:{quote_time[10:12]}:{quote_time[12:14]}"
        )

    return {
        "name": g(1),
        "code": g(2),
        "price": g(3),
        "prev_close": g(4),
        "open": g(5),
        "change": g(31),
        "change_pct": g(32),
        "high": g(33),
        "low": g(34),
        "volume": g(6),
        "amount": g(37) if g(37) else g(35),
        "quote_time": quote_time,
    }


def fetch_quote() -> dict[str, str]:
    resp = requests.get(TENCENT_URL, timeout=15)
    resp.raise_for_status()
    resp.encoding = "gbk"
    return parse_tencent(resp.text)


def excel_path_for(dt: datetime) -> Path:
    return DATA_DIR / f"{dt.strftime('%Y-%m-%d')}.xlsx"


def _hour_key(recorded_at: datetime) -> str:
    return recorded_at.strftime("%Y-%m-%d %H")


def _last_record_hour(ws) -> str | None:
    if ws.max_row < 2:
        return None
    val = ws.cell(row=ws.max_row, column=1).value
    if not val:
        return None
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H")
    return str(val)[:13]


def append_row(path: Path, row: list, recorded_at: datetime) -> bool:
    """Append row; return False if this hour was already recorded."""
    path.parent.mkdir(parents=True, exist_ok=True)
    hour_key = _hour_key(recorded_at)
    if path.exists():
        wb = load_workbook(path)
        ws = wb.active
        if _last_record_hour(ws) == hour_key:
            return False
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "159941"
        ws.append(HEADERS)
    ws.append(row)
    wb.save(path)
    return True


def build_row(recorded_at: datetime, q: dict[str, str]) -> list:
    return [
        recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
        q["name"],
        q["code"],
        _num(q["price"]),
        _num(q["prev_close"]),
        _num(q["open"]),
        _num(q["change"]),
        _num(q["change_pct"]),
        _num(q["high"]),
        _num(q["low"]),
        _int(q["volume"]),
        _num(q["amount"]),
        q["quote_time"],
    ]


def _num(s: str):
    if s is None or s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return s


def _int(s: str):
    if s is None or s == "":
        return None
    try:
        return int(float(s))
    except ValueError:
        return s


def main() -> int:
    parser = argparse.ArgumentParser(description="Track sz159941 into daily Excel")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run even outside Beijing weekday trading hours",
    )
    args = parser.parse_args()

    recorded = now_beijing()
    if not args.force and not in_trading_session(recorded):
        print(
            f"Skip: {recorded.isoformat()} is outside A-share trading hours (use --force to override)",
            file=sys.stderr,
        )
        return 0

    quote = fetch_quote()
    path = excel_path_for(recorded)
    row = build_row(recorded, quote)
    if not append_row(path, row, recorded):
        print(f"Skip: already recorded for hour {_hour_key(recorded)} in {path.name}")
        return 0
    print(f"Appended row to {path.relative_to(REPO_ROOT)}")
    print(
        f"{quote['name']} {quote['code']} price={quote['price']} change_pct={quote['change_pct']}%"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
