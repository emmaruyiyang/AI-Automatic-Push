import requests
import os
from datetime import datetime
from utils import fetch_stock_data

BITABLE_APP_TOKEN = "ZaJGbWgnkaTzchsPwp2clTTlnKb"
BITABLE_TABLE_ID  = "tblCykxhEyIGJwPR"


def get_token(app_id: str, app_secret: str) -> str:
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=10
    )
    return resp.json()["tenant_access_token"]


def insert_records(token: str, records: list[dict]):
    resp = requests.post(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records/batch_create",
        headers={"Authorization": f"Bearer {token}"},
        json={"records": [{"fields": r} for r in records]},
        timeout=15
    )
    data = resp.json()
    if data.get("code") == 0:
        print(f"inserted {len(records)} records successfully")
    else:
        print(f"insert failed: {data}")


def run():
    app_id     = os.environ["FEISHU_APP_ID"]
    app_secret = os.environ["FEISHU_APP_SECRET"]

    rows = fetch_stock_data()
    if not rows:
        print("No stock data fetched, skipping.")
        return

    token = get_token(app_id, app_secret)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    records = []
    for r in rows:
        records.append({
            "日期":          date_str,
            "公司":          f"{r['name']} ({r['ticker']})",
            "股价":          r["price"],
            "涨跌幅":        r["chg_str"],
            "市值":          r["mktcap"],
            "PE (TTM)":      r["pe_ttm"],
            "PE (2026E)":    r["pe_fwd"],
            "EV/Rev (TTM)":  r["ev_rev_ttm"],
            "EV/Rev (2026E)":r["ev_rev_fwd"],
            "收入 (LTM)":    r["revenue"],
            "收入同比":      r["rev_yoy"],
            "毛利率":        r["gross_margin"],
            "净利率":        r["net_margin"],
        })

    insert_records(token, records)


if __name__ == "__main__":
    run()
