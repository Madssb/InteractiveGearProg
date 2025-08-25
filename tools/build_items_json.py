import json
import re

from osrswiki_images import search_many

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
for idx, item in enumerate(items):
    items[0] = handle_levels(item)

items_dict = search_many(items, skip_missing=False)


with open("/home/madssb/InteractiveGearProg/data/generated/items_auto.json", "w") as f:
    json.dump(items_dict, f, indent=2)
