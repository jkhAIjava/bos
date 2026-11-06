# 159941（纳指100 ETF）工作日 hourly 盯盘

本仓库在 **A 股交易日、交易时段内** 自动拉取 **易方达纳斯达克100ETF（代码 sz159941）** 的行情，把 **实时涨跌幅** 等指标写入 Excel，并按天存入 GitHub。

> 说明：`159941` 是在深交所上市的 QDII ETF，跟踪纳斯达克100指数，用于在 A 股交易时段内观察纳指100的参考走势（非美股连续盘）。

## 数据文件

- **目录**：`data/159941/`
- **文件名**：`yyyy-MM-dd.xlsx`（按**北京时间自然日**）
- **同天数据**：向当天文件 **追加** 新行；若同一「小时段」已有记录则 **覆盖该行**（避免重复采集）

### 表格列

| 列名 | 含义 |
|------|------|
| 记录时间 | 写入时的北京时间 |
| 小时段 | `yyyy-MM-dd HH:00`（整点小时，便于按小时对齐） |
| 现价 | 最新价 |
| 昨收 | 昨收价 |
| 涨跌额 | 涨跌金额 |
| 涨跌幅(%) | 涨跌幅百分比 |
| 开盘价 | 开盘价 |
| 行情时间 | 行情源返回的时间 |

行情来源：腾讯财经接口 `qt.gtimg.cn`（`sz159941`）。

## 何时执行（北京时间）

仅在 **工作日**（`chinese_calendar` 判断调休）且处于以下时段才写入：

- 上午：**9:30–11:30**
- 下午：**13:00–15:00**

其余时间脚本会直接跳过，不产生提交。

## 定时方式

1. **GitHub Actions**（`.github/workflows/track-159941.yml`）  
   - 工作日 UTC 多段 cron，覆盖北京交易时段内约 **每小时** 一次拉取  
   - 并对 **11:00、15:00** 附近单独补采（与整点收盘对齐）
2. **Cursor 自动化 cron**（如 `48 * * * *`）  
   - 每小时触发，实际是否写入仍由脚本内交易时段判断

执行脚本：`bash scripts/run_track_and_commit.sh`（安装依赖、拉取 `master`、运行 Python、有变更则提交推送）。

## 本地手动运行

```bash
cd /path/to/bos
bash scripts/run_track_and_commit.sh
```

或直接（不提交）：

```bash
pip install -r scripts/requirements-track.txt
python3 scripts/track_159941.py
```

依赖见 `scripts/requirements-track.txt`（`openpyxl`、`chinese-calendar`）。
