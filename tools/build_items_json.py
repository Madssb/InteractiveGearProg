import json
import re
from pathlib import Path

from osrswiki_images import search_many

ROOT_DIR = Path(__file__).parents[1]
pat = re.compile(r"\d+ (\w+)")


def flatten(xss):
    return [x for xs in xss for x in xs]


def handle_levels(input: str):
    match = pat.match(input)
    if match:
        return match.group(1)
    return input


with open("data/sequence.json", mode="r", encoding="utf-8") as readfile:
    contents = json.load(readfile)

items = flatten(contents)
for idx, item in enumerate(items):
    items[idx] = handle_levels(item)

payload = search_many(items, skip_missing=False)


with open(
    ROOT_DIR / Path("data/generated/items.json"),
    mode="w",
    encoding="utf-8",
) as f:
    json.dump(payload, f, indent=2)
