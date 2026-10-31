#!/usr/bin/env python3
"""Fetch sz159941 (纳指100 ETF) quote and append to daily Excel under data/159941/."""

from __future__ import annotations

import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from chinese_calendar import is_workday
from openpyxl import Workbook, load_workbook

BEIJING = ZoneInfo("Asia/Shanghai")
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "159941"
QUOTE_URL = "https://qt.gtimg.cn/q=sz159941"

HEADERS = ("记录时间", "最新价", "昨收", "涨跌额", "涨跌幅(%)", "行情时间")


def in_trading_window(now: datetime) -> bool:
    if now.tzinfo is None:
        now = now.replace(tzinfo=BEIJING)
    else:
        now = now.astimezone(BEIJING)
    if not is_workday(now.date()):
        return False
    t = now.time()
    from datetime import time

    morning = time(9, 30) <= t < time(12, 0)
    afternoon = time(13, 0) <= t < time(16, 0)
    return morning or afternoon


def fetch_quote() -> dict[str, str | float]:
    req = urllib.request.Request(QUOTE_URL, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=15).read()
    text = None
    for enc in ("gbk", "gb18030", "utf-8"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if not text:
        raise RuntimeError("无法解码行情响应")

    m = re.search(r'"([^"]+)"', text)
    if not m:
        raise RuntimeError("行情响应格式异常")
    parts = m.group(1).split("~")
    if len(parts) < 33:
        raise RuntimeError(f"行情字段不足: {len(parts)}")

    quote_dt = parts[30]
    if len(quote_dt) >= 14:
        quote_display = (
            f"{quote_dt[0:4]}-{quote_dt[4:6]}-{quote_dt[6:8]} "
            f"{quote_dt[8:10]}:{quote_dt[10:12]}:{quote_dt[12:14]}"
        )
    else:
        quote_display = quote_dt

    return {
        "name": parts[1],
        "code": parts[2],
        "price": float(parts[3]),
        "prev_close": float(parts[4]),
        "change": float(parts[31]),
        "change_pct": float(parts[32]),
        "quote_time": quote_display,
    }


def hour_slot(now: datetime) -> str:
    """Same-hour runs upsert on this key (Beijing date + hour)."""
    if now.tzinfo is None:
        now = now.replace(tzinfo=BEIJING)
    else:
        now = now.astimezone(BEIJING)
    return now.strftime("%Y-%m-%d %H:00")


def record_time(now: datetime) -> str:
    if now.tzinfo is None:
        now = now.replace(tzinfo=BEIJING)
    else:
        now = now.astimezone(BEIJING)
    return now.strftime("%Y-%m-%d %H:%M:%S")


def append_row(path: Path, row: tuple, slot: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        wb = load_workbook(path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "159941"
        ws.append(HEADERS)

    upsert_row = None
    slot_prefix = slot[:13]  # YYYY-MM-DD HH
    for i in range(2, ws.max_row + 1):
        cell = ws.cell(row=i, column=1).value
        if cell and str(cell)[:13] == slot_prefix:
            upsert_row = i
            break

    if upsert_row is not None:
        for col, val in enumerate(row, start=1):
            ws.cell(row=upsert_row, column=col, value=val)
    else:
        ws.append(list(row))

    wb.save(path)


def main() -> int:
    now = datetime.now(BEIJING)
    if not in_trading_window(now):
        print(f"非 A 股交易时段或节假日，跳过: {now.isoformat()}")
        return 0

    q = fetch_quote()
    day_file = DATA_DIR / f"{now.strftime('%Y-%m-%d')}.xlsx"
    slot = hour_slot(now)
    row = (
        record_time(now),
        q["price"],
        q["prev_close"],
        q["change"],
        q["change_pct"],
        q["quote_time"],
    )
    append_row(day_file, row, slot)
    print(
        f"已写入 {day_file.name}: {q['name']}({q['code']}) "
        f"价={q['price']} 涨跌幅={q['change_pct']}%"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        raise SystemExit(1)
