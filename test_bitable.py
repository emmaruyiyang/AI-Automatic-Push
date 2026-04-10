import requests
from dotenv import load_dotenv
import os

load_dotenv()

APP_ID     = os.environ["FEISHU_APP_ID"]
APP_SECRET = os.environ["FEISHU_APP_SECRET"]
APP_TOKEN  = "ZaJGbWgnkaTzchsPwp2clTTlnKb"
TABLE_ID   = "tblCykxhEyIGJwPR"

# 1. get token
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}
)
token = resp.json().get("tenant_access_token")
print(f"token: {token[:20]}..." if token else f"token error: {resp.json()}")

# 2. try insert one row
resp = requests.post(
    f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records",
    headers={"Authorization": f"Bearer {token}"},
    json={"fields": {"日期": "2026-04-10", "公司": "test"}}
)
print(f"insert result: {resp.json()}")
