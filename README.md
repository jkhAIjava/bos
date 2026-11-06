# 159941（纳指100 ETF）工作日盯盘

本仓库在 **A 股工作日**、**连续竞价时段**（北京时间 9:30–11:30、13:00–15:00）自动抓取 **159941**（深交所纳指100 ETF）行情，将 **实时涨跌幅** 等指标写入 Excel，并推送到本仓库。

## 数据文件

- **路径**：`data/159941/yyyy-MM-dd.xlsx`（按自然日一份）
- **同日数据**：向当日文件 **追加**；若同一 **小时段** 内多次运行，则 **更新该小时对应一行**（避免重复行）
- **列字段**：记录时间、小时段、现价、昨收、涨跌额、涨跌幅(%)、开盘价、行情时间

## 脚本说明

| 文件 | 作用 |
|------|------|
| `scripts/track_159941.py` | 请求腾讯行情接口 `sz159941`，校验是否交易时段与工作日后写入/更新 xlsx |
| `scripts/run_track_and_commit.sh` | 安装依赖、在 `master` 上执行脚本、若有变更则 commit 并 push |
| `scripts/requirements-track.txt` | Python 依赖：`openpyxl`、`chinese-calendar` |

## 定时任务

1. **GitHub Actions**（`.github/workflows/track-159941.yml`）  
   - 工作日（UTC 周一至周五）在覆盖北京交易时段的时间点触发，与脚本内「非交易时段则 skip」一致。  
   - 也可在 Actions 里 **手动运行**（`workflow_dispatch`）。

2. **Cursor 自动化**（若已配置与本仓库关联的 cron）  
   - 与仓库内说明一致时，可每小时触发 `scripts/run_track_and_commit.sh`，脚本在非开盘时段会打印 skip 并正常退出。

## 本地跑一次

```bash
pip install -r scripts/requirements-track.txt
python3 scripts/track_159941.py
```

若在非交易时间执行，会看到 `skip: outside trading window` 且不会修改 xlsx。
