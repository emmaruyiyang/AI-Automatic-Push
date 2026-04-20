# 系统架构说明

## 概览

本系统每天自动采集 AI 资讯、政策新闻和科技股行情，写入飞书多维表格。共三个独立任务，每天美东时间 20:30 并行执行。

---

## 任务一：AI 资讯采集（main.py）

**触发方式**：`python main.py --collect`

**数据源**（`sources.py`）：
- RSS：OpenAI、Anthropic、DeepMind、arXiv、TechCrunch 等 40+ 源
- 网页爬取：Krea、Pika、Higgsfield 等应用层网站
- Twitter/X：Sam Altman、Karpathy、Lilian Weng 等 KOL

**数据流**：
1. 抓取过去 24 小时内容（RSS 用 `published_parsed`，网页用 `<time>` 标签或正文日期）
2. 清洗：去除 HTML 标签、过滤导航链接、获取文章正文
3. 写入飞书多维表格 `tblB5hwdtlejr1xg`

**字段**：`title`, `url`, `summary`, `source`, `category`, `pub_time`, `source_type`

**Category 值**：`model` / `biz` / `tech` / `creative` / `social` / `funding` / `public_market` / `opinion` / `research`

---

## 任务二：政策新闻采集（push_policy.py）

**触发方式**：`python push_policy.py`

**数据源**（`sources_policy.py`）：
- RSS：求是、新华社、人民日报、CF40、钛媒体、澎湃、财新等 13 源
- 网页爬取：金融四十人论坛、国务院政策 等 2 源（无 RSS 的兜底）

**数据流**：
1. 抓取过去 24 小时内容
2. 网页抓取：仅保留能识别发布日期的文章链接，获取全文
3. 写入飞书多维表格 `tblW0ZKtC5yAeVFC`

**字段**：同任务一

**Category 值**：`news` / `deep` / `media` / `gov`

---

## 任务三：股票行情推送（push_stock.py）

**触发方式**：`python push_stock.py`

**数据源**：`yfinance`（实时拉取）

**标的**：Google (GOOGL)、Meta (META)、NVIDIA (NVDA)、MSFT、Adobe (ADBE)

**数据流**：
1. 拉取当日股价、估值倍数、财务数据
2. 写入飞书多维表格 `tblCykxhEyIGJwPR`

**字段**：`日期`, `公司`, `股价`, `涨跌幅`, `市值`, `PE (TTM)`, `PE (2026E)`, `EV/Rev (TTM)`, `EV/Rev (2026E)`, `收入 (LTM)`, `收入同比`, `毛利率`, `净利率`

---

## 公共模块

| 文件 | 职责 |
|------|------|
| `feishu_bitable.py` | 飞书 tenant token 获取（带缓存）+ 单条记录写入 |
| `utils.py` | yfinance 数据拉取、数字格式化函数 |

---

## 定时任务

通过 `crontab` 设置，每天 UTC 01:30（美东 20:30）三个任务同时触发：

```
30 1 * * * cd <项目目录> && python3 push_policy.py >> logs/policy.log 2>&1
30 1 * * * cd <项目目录> && python3 main.py --collect >> logs/main.log 2>&1
30 1 * * * cd <项目目录> && python3 push_stock.py >> logs/stock.log 2>&1
```

日志路径：`logs/policy.log`、`logs/main.log`、`logs/stock.log`

---

## 飞书多维表格

| 表格 | TABLE_ID | 用途 |
|------|----------|------|
| AI 资讯 | `tblB5hwdtlejr1xg` | main.py 写入 |
| 政策新闻 | `tblW0ZKtC5yAeVFC` | push_policy.py 写入 |
| 股票行情 | `tblCykxhEyIGJwPR` | push_stock.py 写入 |

Base APP_TOKEN：`ZaJGbWgnkaTzchsPwp2clTTlnKb`
