#!/usr/bin/env python3
"""Fetch sz159941 (纳指100 ETF) quote and append to daily Excel under data/159941/."""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    import chinese_calendar as calendar
except ImportError:
    calendar = None

try:
    from openpyxl import Workbook, load_workbook
except ImportError:
    print("Missing openpyxl; run: pip install -r requirements-track.txt", file=sys.stderr)
    sys.exit(2)

BEIJING = ZoneInfo("Asia/Shanghai")
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "159941"
QUOTE_URL = "https://qt.gtimg.cn/q=sz159941"

HEADERS = ("时间", "名称", "代码", "现价", "昨收", "涨跌额", "涨跌幅(%)", "数据来源")


def is_trading_session(now: datetime) -> bool:
    if now.tzinfo is None:
        now = now.replace(tzinfo=BEIJING)
    else:
        now = now.astimezone(BEIJING)

    if calendar is not None:
        if not calendar.is_workday(now.date()):
            return False
    else:
        if now.weekday() >= 5:
            return False

    t = now.time()
    morning = time(9, 30) <= t <= time(11, 30)
    afternoon = time(13, 0) <= t <= time(15, 0)
    return morning or afternoon


def fetch_quote() -> dict:
    req = urllib.request.Request(QUOTE_URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        raw = urllib.request.urlopen(req, timeout=15).read()
    except urllib.error.URLError as e:
        raise RuntimeError(f"quote request failed: {e}") from e

    text = raw.decode("gbk", errors="replace")
    m = re.search(r'v_sz159941="([^"]+)"', text)
    if not m:
        raise RuntimeError("unexpected quote response")

    parts = m.group(1).split("~")
    if len(parts) < 33:
        raise RuntimeError(f"incomplete quote fields ({len(parts)})")

    ts_raw = parts[30]
    quote_time = datetime.strptime(ts_raw, "%Y%m%d%H%M%S").replace(tzinfo=BEIJING)

    return {
        "quote_time": quote_time,
        "name": parts[1],
        "code": parts[2],
        "price": float(parts[3]),
        "prev_close": float(parts[4]),
        "change": float(parts[31]),
        "change_pct": float(parts[32]),
        "source": "qt.gtimg.cn",
    }


def hour_key(dt: datetime) -> str:
    dt = dt.astimezone(BEIJING)
    return dt.strftime("%Y-%m-%d %H:00")


def row_from_quote(q: dict) -> tuple:
    t = q["quote_time"].astimezone(BEIJING).strftime("%Y-%m-%d %H:%M:%S")
    return (
        t,
        q["name"],
        q["code"],
        q["price"],
        q["prev_close"],
        q["change"],
        q["change_pct"],
        q["source"],
    )


def append_to_excel(q: dict) -> Path:
    day = q["quote_time"].astimezone(BEIJING).strftime("%Y-%m-%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{day}.xlsx"
    new_row = row_from_quote(q)
    dedupe = hour_key(q["quote_time"])

    if path.exists():
        wb = load_workbook(path)
        ws = wb.active
        existing_hours = set()
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and row[0]:
                try:
                    dt = datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=BEIJING)
                    existing_hours.add(hour_key(dt))
                except ValueError:
                    continue
        if dedupe in existing_hours:
            for idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
                cell = row[0].value
                if not cell:
                    continue
                try:
                    dt = datetime.strptime(str(cell), "%Y-%m-%d %H:%M:%S").replace(tzinfo=BEIJING)
                except ValueError:
                    continue
                if hour_key(dt) == dedupe:
                    for col, val in enumerate(new_row, start=1):
                        ws.cell(row=idx, column=col, value=val)
                    break
        else:
            ws.append(list(new_row))
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "159941"
        ws.append(list(HEADERS))
        ws.append(list(new_row))

    wb.save(path)
    return path


def main() -> int:
    now = datetime.now(BEIJING)
    if not is_trading_session(now):
        print(f"skip: outside trading session ({now.strftime('%Y-%m-%d %H:%M %Z')})")
        return 0

    q = fetch_quote()
    path = append_to_excel(q)
    print(
        f"ok: {q['name']} {q['code']} "
        f"price={q['price']} change_pct={q['change_pct']}% -> {path.relative_to(REPO_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1)
