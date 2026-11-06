# 159941（纳指 100 ETF）工作日盯盘记录

本仓库通过 **GitHub Actions** 在中国 A 股**工作日**的**交易时段**内，按固定时间表抓取 **易方达纳斯达克 100ETF（代码 159941，深市 `sz159941`）** 的行情（含相对昨收的**实时涨跌幅**），并写入 Excel。

> 说明：标的为跟踪纳斯达克 100 的 **ETF**，数据来源为腾讯行情接口，非境外指数官方点位。

## 数据位置

- 目录：`data/159941/`
- 文件命名：按**北京日期**，`yyyy-MM-dd.xlsx`（例如 `2026-11-06.xlsx`）
- **同一天**多次运行会在**同一文件**中**追加**一行；若同一「小时段」重复运行则**更新**该行（见下表「小时段」列）

## 定时任务（GitHub Actions）

工作流：`.github/workflows/track-159941.yml`

- **触发**：`workflow_dispatch`（可手动运行）+ `schedule`（Cron，按 UTC，北京时间需 +8）
- **工作日**：脚本内使用 `chinese-calendar` 判断**中国工作日**（跳过周末与部分调休节假日）
- **交易时段**（北京时间）：上午 `9:30–11:30`，下午 `13:00–15:00`；非该时段运行会跳过、不写表

Cron 与交易时段对齐（含上午收盘前 `11:00`、下午收盘 `15:00` 的整点补采），在一天内**覆盖每个交易小时段**的采样。

## 本地或手动运行

```bash
pip install -r scripts/requirements-track.txt
python3 scripts/track_159941.py
```

在 CI 中由 `scripts/run_track_and_commit.sh` 安装依赖、切到 `master`、运行脚本并在 `data/159941/` 有变更时提交推送。

## 启用前检查

1. 仓库 **Settings → Actions → General**：允许 **Read and write**（本 workflow 已设 `permissions: contents: write`）。
2. **默认分支**为 `master`（脚本向 `master` 提交行情文件）。
3. 首次可在 **Actions** 里打开 **Track 159941 hourly** → **Run workflow** 试跑。
