import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Set

from osrswiki_images import search_many

ROOT_DIR = Path(__file__).parents[1]
pat = re.compile(r"\d+ (\w+)")

WIKI_W = "https://oldschool.runescape.wiki/w/"
WIKI_IMG = "https://oldschool.runescape.wiki/images/"
IMG_EXT_RE = re.compile(r"\.(png|gif|jpg|jpeg|webp)$", re.IGNORECASE)


def flatten(xss):
    return [x for xs in xss for x in xs]


def handle_levels(input: str):
    match = pat.match(input)
    if match:
        return match.group(1)
    return input


def sanitize_name_for_url(name: str) -> str:
    # Loose normalization to match typical wiki page path
    return name.strip().replace(" ", "_")


def is_valid_record(rec: Dict[str, str]) -> bool:
    if not isinstance(rec, dict):
        return False
    wiki = rec.get("wikiUrl")
    img = rec.get("imgUrl")
    if not (isinstance(wiki, str) and isinstance(img, str)):
        return False
    if not (wiki.startswith(WIKI_W) and img.startswith(WIKI_IMG)):
        return False
    if not IMG_EXT_RE.search(img):
        return False
    return True


def load_json(path: Path) -> List:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fetch_sequence_vals() -> List[str]:
    sequence = load_json(ROOT_DIR / Path("data/sequence.json"))
    retirement = load_json(ROOT_DIR / Path("data/retirement.json"))
    all = sequence + retirement
    items = flatten(all)
    items = [s.lstrip("*") for s in items]
    for idx, item in enumerate(items):
        items[idx] = handle_levels(item)
    return items


def remove_filtered(sequence, filter_list):
    result = []
    for item in sequence:
        if isinstance(item, list):
            # Recurse into sublists
            cleaned = remove_filtered(item, filter_list)
            if cleaned:  # only keep non-empty sublists
                result.append(cleaned)
        elif isinstance(item, str):
            # Only keep strings not in filter_list
            if item not in filter_list:
                result.append(item)
        else:
            # Preserve unexpected non-list, non-str items as-is
            result.append(item)
    return result


def update_bare_bones():
    sequence = load_json(ROOT_DIR / Path("data/sequence.json"))
    filter = load_json(ROOT_DIR / Path("data/filter.json"))
    sequence_bare_bones = remove_filtered(sequence, filter)

    out = ROOT_DIR / Path("data/generated/sequence-bare-bones.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(sequence_bare_bones, f, indent=2, ensure_ascii=False)


def build_worklist(
    sequence_names: Iterable[str], cache: Dict[str, Dict[str, str]]
) -> List[str]:
    """Compare sequence names against cache keys to infer workload. also parse for invalid records to pad out workload with."""
    work: List[str] = []
    for name in sequence_names:
        rec = cache.get(name)
        if rec is None or not is_valid_record(rec):
            work.append(name)
    return work


def update_items_cache():
    """Compare sequence.json item names against items.json keys to infer osrswiki api requests to
    make. Also parse for invalid records. make api requests, update items with results.
    """
    sequence = fetch_sequence_vals()
    items = load_json(ROOT_DIR / Path("data/generated/items.json"))
    worklist = build_worklist(sequence, items)
    payload = search_many(worklist, skip_missing=False)
    for k, v in payload.items():
        if v is not None:  # only merge successful resolves
            items[k] = v
    out = ROOT_DIR / Path("data/generated/items.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    update_items_cache()
    update_bare_bones()
