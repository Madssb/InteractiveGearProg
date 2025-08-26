import json
import os
from datetime import date, timedelta
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    pass

API_KEY = os.getenv("GOATCOUNTER_API_KEY")
if not API_KEY:
    raise SystemExit("GOATCOUNTER_API_KEY is not set")

ROOT_DIR = Path(__file__).parents[1]

base = "https://ladlor0interactive0prog.goatcounter.com/api/v0/stats/total"
end = date.today()
start = end - timedelta(days=31)

resp = requests.get(
    base,
    params={"start": start.isoformat(), "end": end.isoformat()},
    headers={"Authorization": f"Bearer {GOATCOUNTER_API_KEY}"},
    timeout=10,
)
resp.raise_for_status()
data = resp.json()
monthly_viewcount = data.get("total")
payload = {"viewcountMonth": monthly_viewcount}

with open(
    ROOT_DIR / Path("data/generated/count.json"),
    mode="w",
    encoding="utf-8",
) as f:
    json.dump(payload, f)
