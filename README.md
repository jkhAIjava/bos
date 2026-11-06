# 159941（纳指 100 ETF）工作日盯盘

本仓库在 **A 股工作日、沪深交易时段**（北京时间 9:30–11:30、13:00–15:00）按约 **每小时** 拉取一次场外纳指 ETF **159941**（腾讯行情 `sz159941`）的行情，将 **实时涨跌幅** 等字段写入 `data/159941/yyyy-MM-dd.xlsx`。

## 数据文件

| 项目 | 说明 |
|------|------|
| 路径 | `data/159941/yyyy-MM-dd.xlsx`（按**自然日**区分） |
| 同一天 | **追加**：每个**小时段**一行；同一小时段再次运行会**更新**该行（不重复插行） |
| 列含义 | 记录时间、小时段、现价、昨收、涨跌额、涨跌幅(%)、开盘价、行情时间 |

## 定时任务（两处互补）

1. **GitHub Actions**（`.github/workflows/track-159941.yml`）  
   - 在 GitHub 云端按 cron 执行，成功后自动 `git commit` / `push` 到 `master`。  
   - 需仓库 **Actions** 已启用，且默认分支写权限正常（工作流已设 `contents: write`）。

2. **Cursor 自动化**  
   - Cron：`48 * * * *`（每小时 :48），执行 `scripts/run_track_and_commit.sh`。  
   - 脚本在非交易时段会打印 `skip` 并正常退出。

非交易日、午休、收盘后脚本会直接跳过，不会改动表格。

## 本地手动运行

```bash
pip install -r scripts/requirements-track.txt
python3 scripts/track_159941.py
```

若在交易时段外测试，会提示 `skip`。也可使用与线上相同的提交流程：

```bash
bash scripts/run_track_and_commit.sh
```

## 说明

- 标的 **159941** 为 A 股上市的纳指 100 相关 ETF，行情时间与涨跌幅随 **沪深交易时间**，与美股夜盘不同时区。  
- 工作日判断依赖 `chinese-calendar`（含调休）。
