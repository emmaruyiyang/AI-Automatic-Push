# AI 资讯推送机器人

每天自动采集 AI 资讯、政策新闻、科技股行情，写入飞书多维表格。

## 安装

```bash
pip install -r requirements.txt
```

配置 `.env`：

```
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

## 运行

```bash
# AI 资讯采集 → 飞书多维表格
python main.py --collect

# 政策新闻采集 → 飞书多维表格
python push_policy.py

# 股票行情推送 → 飞书多维表格
python push_stock.py
```

## 定时任务

已通过 `crontab` 配置，每天美东时间 20:30 自动执行，日志写入 `logs/`。

查看当前任务：

```bash
crontab -l
```

## 内容板块

| 任务 | 数据源 | 飞书表格 |
|------|--------|----------|
| `main.py` | OpenAI/Anthropic/arXiv/Twitter 等 40+ 源 | AI 资讯表 |
| `push_policy.py` | 新华社/人民日报/CF40/财新 等 15 源 | 政策新闻表 |
| `push_stock.py` | yfinance（GOOGL/META/NVDA/MSFT/ADBE） | 股票行情表 |

详细架构说明见 [ARCHITECTURE.md](ARCHITECTURE.md)。
