import requests
import os
import json
from utils import fetch_stock_data, build_stock_elements

def run():
    rows = fetch_stock_data()
    if not rows:
        print("No stock data fetched, skipping push.")
        return

    elements = build_stock_elements(rows)
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "📈 二级市场行情"},
                "template": "blue"
            },
            "elements": elements
        }
    }

    print(json.dumps(card, ensure_ascii=False, indent=2))

    resp = requests.post(
        os.environ["FEISHU_WEBHOOK"],
        json=card,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    data = resp.json()
    if data.get("code") == 0 or data.get("StatusCode") == 0:
        print("pushed successfully")
    else:
        print(f"push failed: {data}")

if __name__ == "__main__":
    run()
