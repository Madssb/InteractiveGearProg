import json
from pathlib import Path

from osrswiki_images import search_many

ROOT_DIR = Path(__file__).parents[1]
BANK_JSON = ROOT_DIR / Path("data/bank.json")

header_items = [
    "crystal helm",
    "Amulet of glory",
    "Magic secateurs",
    "Oak logs",
    "Tanzanite fang",
    "Dragon Plateskirt",
    "Harralander tar",
    "Saradomin brew",
    "expert mining gloves",
]


if not BANK_JSON.exists():
    contents = {}
try:
    with BANK_JSON.open("r", encoding="utf-8") as f:
        contents = json.load(f)
except json.decoder.JSONDecodeError:
    contents = {}
bank_header = {}


payload = search_many(header_items)
bank_header["0"] = "/data/external/infinity_symbol.png"
for idx, val in enumerate(payload.values()):
    bank_header[str(idx + 1)] = val["imgUrl"]

contents["header"] = bank_header
with BANK_JSON.open("w", encoding="utf-8") as f:
    json.dump(contents, f, indent=2, ensure_ascii=False)
