import json
import os
import time
from datetime import date, timedelta
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    pass

GOATCOUNTER_API_KEY = os.getenv("GOATCOUNTER_API_KEY")
if not GOATCOUNTER_API_KEY:
    raise SystemExit("GOATCOUNTER_API_KEY is not set")

ROOT_DIR = Path(__file__).parents[1]

base = "https://ladlor0interactive0prog.goatcounter.com/api/v0/stats/total"
headers = {"Authorization": f"Bearer {GOATCOUNTER_API_KEY}"}


def fetch_total(start: date, end: date):
    params = {"start": start.isoformat(), "end": end.isoformat()}
    print(f"[goatcounter] requesting total start={params['start']} end={params['end']}")
    response = requests.get(base, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("total")


def fetch_with_retry(start: date, end: date, attempts: int = 3):
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return fetch_total(start, end)
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code if error.response else None
            # 404 can happen intermittently for date windows including "today".
            if status_code == 404 and end == date.today():
                print(
                    "[goatcounter] got 404 for window including today; "
                    "retrying with end=yesterday"
                )
                return fetch_total(start, end - timedelta(days=1))
            # Retry only transient server-side issues.
            if status_code not in (429, 500, 502, 503, 504) or attempt == attempts:
                raise
            last_error = error
        except requests.exceptions.RequestException as error:
            last_error = error
            if attempt == attempts:
                raise
        time.sleep(min(2**attempt, 10))

    # Defensive; loop should have returned or raised.
    if last_error:
        raise last_error
    raise RuntimeError("Unexpected retry flow in goatcounter fetch")


end = date.today() - timedelta(days=1)
start = end - timedelta(days=31) - timedelta(days=1)
monthly_viewcount = fetch_with_retry(start, end)
print(f"[goatcounter] monthly total fetched: {monthly_viewcount}")
payload = {"viewCountMonth": monthly_viewcount}

with open(
    ROOT_DIR / Path("data/generated/count.json"),
    mode="w",
    encoding="utf-8",
) as f:
    json.dump(payload, f)
