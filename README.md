# 159941（纳指 ETF）工作日盯盘

本仓库在 **A 股交易日、交易时段** 内每小时采集一次 **易方达纳斯达克 100 交易型开放式指数证券投资基金（场内简称常关联纳指 ETF，代码 `159941` / `sz159941`）** 的腾讯行情快照，写入按自然日区分的 Excel，并推送到 `master`。

## 数据文件

| 项目 | 说明 |
|------|------|
| 目录 | `data/159941/` |
| 文件名 | `yyyy-MM-dd.xlsx`（北京时间自然日） |
| 同天写入 | **同一「小时段」内多次运行会更新该行**；新的整点小时段会**追加**新行 |

表头字段：`记录时间`、`小时段`、`现价`、`昨收`、`涨跌额`、`涨跌幅(%)`、`开盘价`、`行情时间`。

## 交易时段判定

使用 `chinese-calendar` 判断是否为 **中国工作日**，并仅在以下北京时间内写入（其余运行会直接退出且不改文件）：

- 上午：**09:30–11:30**
- 下午：**13:00–15:00**

## 定时如何触发

1. **GitHub Actions**（`.github/workflows/track-159941.yml`）  
   - 工作日按 cron 调用 `scripts/run_track_and_commit.sh`，与北京时间交易时段对齐（含 11:00、15:00 附近补采），详见该文件内注释。

2. **Cursor 自动化**（若已配置）  
   - 可按需每小时执行同一脚本：`bash scripts/run_track_and_commit.sh`（与仓库内说明一致时，通常为每时 `:48` UTC 等）。

脚本会先安装 `scripts/requirements-track.txt` 中的依赖，再执行 `scripts/track_159941.py`，若有 `data/159941/*.xlsx` 变更则提交并 `git push origin master`。

## 本地手动跑一次

```bash
cd /path/to/bos
bash scripts/run_track_and_commit.sh
```

仅在当前时间处于上述交易窗口且为工作日时才会更新表格；否则脚本内 Python 会打印 `skip` 并正常退出。

## 依赖

- Python 3  
- `openpyxl`、`chinese-calendar`（由 `scripts/requirements-track.txt` 固定）
