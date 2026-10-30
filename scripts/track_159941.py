#!/usr/bin/env python3
"""Fetch sz159941 (纳指100 ETF) quote and append to daily Excel under data/."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from chinese_calendar import is_workday
from openpyxl import Workbook, load_workbook

TZ = ZoneInfo("Asia/Shanghai")
CODE = "159941"
TENCENT_URL = f"https://qt.gtimg.cn/q=sz{CODE}"
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "159941"

HEADERS = [
    "记录时间",
    "代码",
    "名称",
    "最新价",
    "昨收",
    "开盘",
    "涨跌额",
    "涨跌幅(%)",
    "行情时间",
]


def now_sh() -> datetime:
    return datetime.now(TZ)


def is_trading_session(when: datetime) -> bool:
    if not is_workday(when.date()):
        return False
    t = when.time()
    morning = time(9, 30) <= t <= time(11, 30)
    afternoon = time(13, 0) <= t <= time(15, 0)
    return morning or afternoon


def fetch_quote() -> dict[str, str | float]:
    req = urllib.request.Request(
        TENCENT_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; bos-track/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("gbk", "replace")
    m = re.search(r'v_sz\d+="([^"]+)"', raw)
    if not m:
        raise RuntimeError(f"无法解析行情响应: {raw[:120]!r}")
    parts = m.group(1).split("~")
    if len(parts) < 33:
        raise RuntimeError(f"行情字段不足: {len(parts)}")

    quote_time_raw = parts[30]
    if len(quote_time_raw) == 14:
        quote_time = datetime.strptime(quote_time_raw, "%Y%m%d%H%M%S").replace(tzinfo=TZ)
    else:
        quote_time = now_sh()

    return {
        "name": parts[1],
        "code": parts[2],
        "price": float(parts[3]),
        "prev_close": float(parts[4]),
        "open": float(parts[5]),
        "change": float(parts[31]),
        "change_pct": float(parts[32]),
        "quote_time": quote_time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def excel_path(for_date: datetime) -> Path:
    return DATA_DIR / f"{for_date.strftime('%Y-%m-%d')}.xlsx"


def append_row(path: Path, row: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        wb = load_workbook(path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "159941"
        ws.append(HEADERS)
    ws.append(row)
    wb.save(path)


def run(force: bool = False) -> int:
    when = now_sh()
    if not force and not is_trading_session(when):
        print(f"非 A 股交易时段或非交易日，跳过: {when.isoformat()}")
        return 0

    quote = fetch_quote()
    row = [
        when.strftime("%Y-%m-%d %H:%M:%S"),
        quote["code"],
        quote["name"],
        quote["price"],
        quote["prev_close"],
        quote["open"],
        quote["change"],
        quote["change_pct"],
        quote["quote_time"],
    ]
    path = excel_path(when)
    append_row(path, row)
    print(
        f"已写入 {path.relative_to(ROOT)}: "
        f"{quote['name']} 涨跌幅 {quote['change_pct']}% @ {quote['price']}"
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="盯盘 159941 并追加每日 Excel")
    parser.add_argument(
        "--force",
        action="store_true",
        help="忽略交易时段检查（用于手动测试）",
    )
    args = parser.parse_args()
    try:
        raise SystemExit(run(force=args.force))
    except urllib.error.URLError as e:
        print(f"拉取行情失败: {e}", file=sys.stderr)
        raise SystemExit(1) from e
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
