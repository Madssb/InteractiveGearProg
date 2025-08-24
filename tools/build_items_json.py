import json
import re
from pathlib import Path
from time import sleep

from osrswiki_images import search_all

items_filepath: Path = Path(__file__).parent / Path("../data/items_auto.json")
items_json: dict = {}
pat = re.compile(r"\d+ (\w+)")

with open("data/sequence.json", mode="r", encoding="utf-8") as readfile:
    contents = json.load(readfile)


def flatten(xss):
    return [x for xs in xss for x in xs]


def handle_levels(input: str):
    match = pat.match(input)
    if match:
        return match.group(1)
    return input


items = flatten(contents)
for item in items:
    item = handle_levels(item)
    if item in items_json.keys():
        print("already in dict: ", item)
        continue
    sleep(0.2)
    entry = search_all(item)
    if entry:
        print("success: ", item)
    else:
        print("failed: ", item)

    items_json.update({item: entry})

with open(items_filepath, "w") as f:
    json.dump(items_json, f)
