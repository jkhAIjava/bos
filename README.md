# 159941（纳指 ETF）工作日每小时行情记录

本仓库通过 **GitHub Actions** 在 A 股交易日、交易时段内按约每小时抓取 **159941（纳斯达克 100 指数 ETF，深市代码 `sz159941`）** 的实时涨跌幅等行情，写入 Excel，并推送到本仓库。

## 工作原理

| 项目 | 说明 |
|------|------|
| **调度** | 工作流：`.github/workflows/track-159941.yml`（工作日 `workflow_dispatch` 可手动触发） |
| **交易时段** | 北京时间 9:30–11:30、13:00–15:00；节假日以中国工作日为准（`chinese-calendar`） |
| **数据文件** | `data/159941/yyyy-MM-dd.xlsx`，**同一天内多条记录为追加/按「小时段」更新**（同一小时段重复运行会覆盖该小时行） |
| **脚本** | `scripts/track_159941.py`（腾讯行情接口）、`scripts/run_track_and_commit.sh`（安装依赖、拉取 `master`、提交推送） |

Excel 列包括：记录时间、小时段、现价、昨收、涨跌额、涨跌幅(%)、开盘价、行情时间。

## 使用前请确认

1. 在 GitHub 仓库 **Settings → Actions → General** 中启用 Actions，且允许工作流写入仓库内容（本 workflow 已设置 `contents: write`）。
2. 默认数据会提交到 **`master`** 分支（脚本中会 `checkout master` 再提交）。

## 本地试跑（可选）

```bash
pip install -r scripts/requirements-track.txt
python3 scripts/track_159941.py
```

仅在交易时段内会写入文件；非交易时段会打印 `skip` 并退出 0。

## 手动执行

在 GitHub 打开 **Actions → Track 159941 hourly → Run workflow**，可在任意时间触发；仍仅在交易时段内写入 Excel。
