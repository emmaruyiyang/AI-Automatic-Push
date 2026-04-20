"""
Collect policy news from sources_policy.py and write to Feishu Bitable.
Usage: python push_policy.py
"""

import os
import time
import logging
import feedparser
import requests
from datetime import datetime, timedelta
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
from feishu_bitable import get_tenant_token

load_dotenv()

from sources_policy import RSS_SOURCES, SCRAPE_SOURCES

APP_TOKEN = "ZaJGbWgnkaTzchsPwp2clTTlnKb"
TABLE_ID  = "tblW0ZKtC5yAeVFC"
LOOKBACK_HOURS = 24

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ── Date extraction (same logic as main.py) ──────────────────
import re

DATE_PATTERNS = [
    (r"\b(\d{4}-\d{2}-\d{2})\b",                "%Y-%m-%d"),
    (r"\b([A-Z][a-z]+ \d{1,2},\s+\d{4})\b",     "%B %d, %Y"),
    (r"\b([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})\b", "%b %d, %Y"),
    (r"\b([A-Z][a-z]{2}\d{1,2},\s+\d{4})\b",    "%b%d, %Y"),
]

def _try_parse(text):
    for pat, fmt in DATE_PATTERNS:
        m = re.search(pat, text)
        if m:
            try: return datetime.strptime(m.group(1), fmt)
            except: pass
    return None

def _extract_nearby_time(tag) -> Optional[datetime]:
    node = tag.parent
    for _ in range(6):
        if node is None: break
        t = node.find("time")
        if t and t.get("datetime"):
            try: return datetime.fromisoformat(t["datetime"][:19])
            except: pass
        node = node.parent
    node = tag.parent
    for _ in range(6):
        if node is None: break
        r = _try_parse(node.get_text(" ", strip=True))
        if r: return r
        node = node.parent
    return None


# ── Fetch ─────────────────────────────────────────────────────
def fetch_rss(source: dict, since: datetime) -> list[dict]:
    items = []
    try:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries:
            pub = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                pub = datetime(*entry.updated_parsed[:6])
            if pub and pub < since:
                continue
            title = getattr(entry, "title", "")
            link  = getattr(entry, "link", "")
            if hasattr(entry, "content") and entry.content:
                raw = entry.content[0].get("value", "")
            else:
                raw = getattr(entry, "summary", "")
            try:
                summary = BeautifulSoup(raw, "html.parser").get_text(" ", strip=True)
            except Exception:
                summary = raw
            items.append({
                "title":       title,
                "url":         link,
                "summary":     summary,
                "source":      source["name"],
                "category":    source["category"],
                "pub_time":    pub.strftime("%m-%d %H:%M") if pub else "",
                "source_type": "rss",
            })
    except Exception as e:
        log.warning(f"RSS抓取失败 {source['name']}: {e}")
    return items


NAV_KEYWORDS = {"pricing","login","signup","sign-up","register","contact",
                "about","careers","terms","privacy","faq","help","home",
                "features","api","docs","explore","tag","category"}

def fetch_webpage(source: dict, since: datetime) -> list[dict]:
    items = []
    try:
        resp = requests.get(source["url"], timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        seen = set()
        for a in soup.find_all("a", href=True)[:200]:
            title = a.get_text(strip=True)
            href  = a["href"]
            if not href.startswith("http"):
                href = urljoin(source["url"], href)
            if len(title) <= 15: continue
            if any(kw in href.lower() for kw in NAV_KEYWORDS): continue
            if href in seen: continue
            seen.add(href)
            pub_time = _extract_nearby_time(a)
            if not pub_time: continue
            if pub_time < since: continue
            body = ""
            try:
                ar = requests.get(href, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                as_ = BeautifulSoup(ar.text, "html.parser")
                for tag in as_(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                body = as_.get_text(" ", strip=True)
            except Exception:
                pass
            items.append({
                "title":       title,
                "url":         href,
                "summary":     body,
                "source":      source["name"],
                "category":    source["category"],
                "pub_time":    pub_time.strftime("%m-%d %H:%M"),
                "source_type": "webpage",
            })
    except Exception as e:
        log.warning(f"网页抓取失败 {source['name']}: {e}")
    return items


# ── Write to Bitable ──────────────────────────────────────────
def _insert_record(token: str, fields: dict) -> bool:
    resp = requests.post(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"fields": fields},
        timeout=10,
    )
    data = resp.json()
    if data.get("code") == 0:
        return True
    log.warning(f"Bitable insert failed: {data}")
    return False


def write_to_bitable(items: list[dict]):
    if not items:
        return
    token = get_tenant_token()
    success = 0
    for item in items:
        pub_time_ms = None
        pt = item.get("pub_time", "")
        if pt:
            try:
                year = datetime.now().year
                dt = datetime.strptime(f"{year}-{pt}", "%Y-%m-%d %H:%M")
                pub_time_ms = int(dt.timestamp() * 1000)
            except Exception:
                pass
        fields = {
            "title":       item.get("title", ""),
            "url":         item.get("url", ""),
            "summary":     item.get("summary", ""),
            "source":      item.get("source", ""),
            "category":    item.get("category", ""),
            "pub_time":    pub_time_ms,
            "source_type": item.get("source_type", ""),
        }
        if _insert_record(token, fields):
            success += 1
        time.sleep(0.05)
    log.info(f"写入完成: {success}/{len(items)}")


# ── Main ──────────────────────────────────────────────────────
def run():
    since = datetime.now() - timedelta(hours=LOOKBACK_HOURS)
    all_items = []

    for src in RSS_SOURCES:
        items = fetch_rss(src, since)
        all_items.extend(items)
        log.info(f"  RSS {src['name']}: {len(items)}条")
        time.sleep(0.5)

    for src in SCRAPE_SOURCES:
        items = fetch_webpage(src, since)
        all_items.extend(items)
        log.info(f"  Web {src['name']}: {len(items)}条")
        time.sleep(0.5)

    log.info(f"共采集 {len(all_items)} 条，开始写入...")
    write_to_bitable(all_items)


if __name__ == "__main__":
    run()
