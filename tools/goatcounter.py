import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import requests

parser = argparse.ArgumentParser()
parser.add_argument("key")
args = parser.parse_args()
goatcounter_api_key = args.key

ROOT_DIR = Path(__file__).parents[1]

base = "https://ladlor0interactive0prog.goatcounter.com/api/v0/stats/total"
end = date.today()
start = end - timedelta(days=31)

resp = requests.get(
    base,
    params={"start": start.isoformat(), "end": end.isoformat()},
    headers={"Authorization": f"Bearer {goatcounter_api_key}"},
    timeout=10,
)
resp.raise_for_status()
data = resp.json()
monthly_viewcount = data.get("total")
payload = {"viewcountMonth": monthly_viewcount}

with open(
    ROOT_DIR / Path("generated/count.json"),
    mode="w",
    encoding="utf-8",
) as f:
    json.dump(payload, f)
