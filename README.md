# 159941（纳指 100 ETF）盯盘数据

本仓库在工作日 **A 股交易时段**内定期拉取 **易方达纳斯达克 100ETF（`sz159941`）** 的行情（含**涨跌幅**等），并写入 Excel 后推送到本仓库。

## 数据文件

- **目录**：`data/159941/`
- **文件名**：`yyyy-MM-dd.xlsx`（按**北京时间**自然日）
- **同一天**：按「**小时段**」一行；若同一小时内多次运行，会**覆盖该行**（不会重复追加多行）。

表头包括：记录时间、小时段、现价、昨收、涨跌额、**涨跌幅(%)**、开盘价、行情时间。

## 交易时段（北京时间）

仅以下时段会写入（法定节假日调休以中国工作日历 `chinese-calendar` 为准）：

- 上午 **9:30–11:30**
- 下午 **13:00–15:00**

其余时间脚本会直接退出，不产生提交。

## 定时如何触发

1. **GitHub Actions**（`/.github/workflows/track-159941.yml`）  
   在仓库 **Settings → Actions → General** 中启用 Actions，工作流会按排程在交易日触发并执行 `scripts/run_track_and_commit.sh`（安装依赖、运行脚本、若有变更则 commit 到 `master`）。

2. **其他自动化 / 本机**  
   可在工作日交易时段内**每小时**调用同一条命令（与 CI 行为一致）：

   ```bash
   bash scripts/run_track_and_commit.sh
   ```

   依赖见 `scripts/requirements-track.txt`（Python 3 + `openpyxl`、`chinese-calendar`）。

## 行情来源

脚本请求腾讯行情接口 `qt.gtimg.cn`（代码 `sz159941`），仅供参考，不构成投资建议。
