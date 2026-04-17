# import feedparser
# from datetime import datetime, timedelta

# RSSHUB_BASE = "https://rsshub.app"
# LOOKBACK_HOURS = 12

# WECHAT_ACCOUNTS = [
#     {"name": "海外独角兽", "biz": "Mzg2OTY0MDk0NQ=="},
#     {"name": "语言即世界", "biz": "MzE5ODg1MTY4Mw=="},
#     {"name": "机器之心" , "biz": "MzA3MzI4MjgzMw=="}
# ]


# def fetch_wechat(biz: str, name: str, since: datetime) -> list[dict]:
#     url = f"{RSSHUB_BASE}/wechat/mp/article/{biz}"
#     feed = feedparser.parse(url)
#     if feed.bozo:
#         print(f"[{name}] parse error: {feed.bozo_exception}")
#         return []

#     items = []
#     for entry in feed.entries:
#         pub = None
#         if hasattr(entry, "published_parsed") and entry.published_parsed:
#             pub = datetime(*entry.published_parsed[:6])
#         elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
#             pub = datetime(*entry.updated_parsed[:6])
#         if pub and pub < since:
#             continue
#         items.append({
#             "name":     name,
#             "title":    getattr(entry, "title", ""),
#             "url":      getattr(entry, "link", ""),
#             "pub_time": pub.strftime("%m-%d %H:%M") if pub else "unknown",
#         })

#     print(f"[{name}] {len(items)}/{len(feed.entries)} items in window")
#     return items


# if __name__ == "__main__":
#     since = datetime.utcnow() - timedelta(hours=LOOKBACK_HOURS)
#     all_items = []
#     for acct in WECHAT_ACCOUNTS:
#         all_items.extend(fetch_wechat(acct["biz"], acct["name"], since))

#     print(f"\n{len(all_items)} total items")
#     for item in all_items:
#         print(f"[{item['pub_time']}] {item['name']} — {item['title']}\n  {item['url']}")



