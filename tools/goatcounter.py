import os
from datetime import date

import requests
from dotenv import load_dotenv

load_dotenv()
GOATCOUNTER_KEY = os.getenv("GOATCOUNTER_KEY")
if not GOATCOUNTER_KEY:
    raise RuntimeError("GOATCOUNTER_KEY not set")

base = "https://ladlor0interactive0prog.goatcounter.com/api/v0/stats/total"
start = date(2024, 10, 23)
end = date.today()

resp = requests.get(
    base,
    params={"start": start.isoformat(), "end": end.isoformat()},
    headers={"Authorization": f"Bearer {GOATCOUNTER_KEY}"},
    timeout=10,
)
resp.raise_for_status()
data = resp.json()
print("total:", data.get("total"))
