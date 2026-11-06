# 159941（纳指100 ETF）工作日盯盘

本仓库通过 **GitHub Actions** 在 A 股**交易日**的连续竞价时段内多次拉取 **sz159941** 行情，将**实时涨跌幅**等字段**按天追加**到 `data/159941/yyyy-MM-dd.xlsx`。

## 行为说明

- **标的**：深交所 ETF 代码 159941（纳指 100 相关），行情来源为脚本内配置的公开接口。
- **是否运行**：由 `scripts/track_159941.py` 使用 `chinese-calendar` 判断当日是否为中国**工作日**，并判断当前时间是否在 **9:30–11:30、13:00–15:00（北京时间）**；非交易日或非交易时段会直接跳过，不写文件。
- **Excel**：每天一个文件，路径为 `data/159941/yyyy-MM-dd.xlsx`；同一天内按「小时段」列更新：同一小时多次运行会**覆盖该小时行**，不同小时会**追加新行**。
- **提交**：`scripts/run_track_and_commit.sh` 在 CI 中仅在 `data/159941/` 有变更时提交并推送到 `master`。

## 工作流

- 配置文件：`.github/workflows/track-159941.yml`
- 定时：在可能覆盖交易时段的 UTC 时刻触发（含 11:00、15:00 整点补采），具体以 YAML 内注释为准；实际是否写入仍由脚本校验交易日与时段。
- 手动补跑一次：在仓库 **Actions** 中打开「Track 159941 hourly」，使用 **Run workflow**。

## 依赖

- `scripts/requirements-track.txt`：`openpyxl`、`chinese-calendar`

启用本仓库的 **Actions** 且保证默认分支可写后，定时任务即会在云端执行。
