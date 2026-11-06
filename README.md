# 159941（纳指100 ETF）盯盘与 Excel 归档

本仓库通过脚本拉取**易方达纳斯达克100ETF（`sz159941`）**的腾讯行情，在工作日 A 股交易时段将**实时价、涨跌幅等**写入按日划分的 Excel 文件。

## 数据文件

- 路径：`data/159941/yyyy-MM-dd.xlsx`
- 同一天多次运行：**同一「小时段」会更新该行**（避免重复行）；**新小时段会追加新行**。
- 列含：记录时间、小时段、现价、昨收、涨跌额、涨跌幅(%)、开盘价、行情时间。

## 交易时段（北京时间）

仅在下述时间执行写入，其余时间脚本直接退出（不报错）：

- 工作日（`chinese-calendar` 判断中国法定节假日与调休）
- 上午 9:30–11:30、下午 13:00–15:00

## 如何定时运行

1. **GitHub Actions**（推荐）：`.github/workflows/track-159941.yml`  
   - 工作日 UTC 每小时 `:48`（对应北京日间多档采样），并辅以 UTC `3:00`、`7:00` 整点**补采**（对应北京 **11:00**、**15:00** 附近，覆盖午盘末与收盘）。
2. **本地 / 其他调度器**：执行 `bash scripts/run_track_and_commit.sh`  
   - 会先 `pip install -r scripts/requirements-track.txt`，切换到 `master` 拉取最新，运行 `scripts/track_159941.py`，若有 `data/159941/*.xlsx` 变更则提交并推送。

## 本地依赖

```bash
pip install -r scripts/requirements-track.txt
```

（`openpyxl`、`chinese-calendar`。）

## 手动跑一次

```bash
python3 scripts/track_159941.py
```

在交易时段外会看到 `skip: outside trading window`。
