"""
OSRS Wiki resolvers: map game entities to wiki and image URLs.

Network I/O
-----------
- Uses the OSRS Wiki API (`action=bucket` and `action=opensearch`) via a shared
  `requests.Session` with a fixed User-Agent.
- Low-level access: `bucket_query(bucket_name, page_name)`.

Selection and Filtering
-----------------------
- Always selects 'page_name' and one media field.
- Media field: 'icon' for 'infobox_construction'; 'image' for other buckets.
- Applies `default_version=true` where supported (items, construction); falls back
  for items without a default version.
- Page matching is case-insensitive on the API; apostrophes in input are escaped.

Local Data
----------
- `data/prayers.csv` and `data/slayer_rewards.csv` provide filename mappings for
  `prayer()` and `slayer_rewards()`.

Return Conventions
------------------
- High-level resolvers return `{'wikiUrl': str, 'imgUrl': str}` or `None`.
- `bucket_query` returns a `List[Dict[str, str]]` (raw API records) or raises.
- Exceptions: `ConnectionError` on HTTP failure; `KeyError` for unknown bucket.

Public API
----------
- bucket_query(bucket_name, page_name): low-level bucket fetch.
- item(name): item wiki URL and image; prefers default version.
- spell(name): spell wiki URL and image.
- construction(name): construction wiki URL and icon; default version.
- quest(name): quest wiki URL; fixed quest icon.
- skill(name): skill wiki URL and icon; validates known skills.
- slayer_rewards(name): wiki URL and image from local CSV.
- prayer(name): wiki URL and image from local CSV.
- generalized_search(query): fallback OpenSearch resolver.
- search_all(input): tries resolvers in order and returns the first match.

Example
-------
    >>> search_all("Ice Barrage")
    {'wikiUrl': 'https://oldschool.runescape.wiki/w/Ice_Barrage',
     'imgUrl': 'https://oldschool.runescape.wiki/images/...'}
"""

from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests

s = requests.Session()
s.headers.update({"user-agent": "madlor"})
SKILLS = [
    "Attack",
    "Strength",
    "Defence",
    "Ranged",
    "Prayer",
    "Magic",
    "Runecraft",
    "Hitpoints",
    "Crafting",
    "Mining",
    "Smithing",
    "Fishing",
    "Cooking",
    "Firemaking",
    "Woodcutting",
    "Agility",
    "Herblore",
    "Thieving",
    "Fletching",
    "Slayer",
    "Farming",
    "Construction",
    "Hunter",
]
BASE = "https://oldschool.runescape.wiki/"
PRAYERS_CSV = Path(__file__).parent / Path("../data/prayers.csv")
SLAYER_REWARDS_CSV = Path(__file__).parent / Path("../data/slayer_rewards.csv")


def bucket_query(bucket_name: str, page_name: str) -> List[Dict[str, str]]:
    """Requests the OSRS wiki api for the page_name and one of image or icon from case-insensitive
    page name and specified bucket source.

    Sends a GET request to the OSRS wiki api, selecting page name and one of image or icon
    depending on specified bucket; icon for 'infobox_construction', and image otherwise, in
    SQL-like manner. where "page_name" is 'page_name"

    Args:
        bucket_name (str): Name of OSRS wiki api bucket to query.
        page_name (str): Page name in bucket from where to select page_name and/or image or icon.

    Returns:
        List[Dict[str, str]]: Api response;  page name and/or image or icon
    """
    page_name = page_name.replace("'", "\\'")  # handle cases like tumeken's shadow
    query_string = {
        "infobox_item": f"bucket('infobox_item').select('page_name', 'image').where('page_name','{page_name}').where('default_version',true).run()",
        "infobox_item2": f"bucket('infobox_item').select('page_name', 'image').where('page_name','{page_name}').run()",
        "infobox_spell": f"bucket('infobox_spell').select('page_name', 'image').where('page_name','{page_name}').run()",
        "infobox_construction": f"bucket('infobox_construction').select('page_name', 'icon').where('page_name','{page_name}').where('default_version',true).run()",
        "quest": f"bucket('quest').select('page_name').where('page_name','{page_name}').run()",
    }
    params = {
        "action": "bucket",
        "format": "json",
        "query": query_string[bucket_name],
    }
    resp = s.get("https://oldschool.runescape.wiki/api.php", params=params)
    if not resp.ok:
        raise ConnectionError(f"request failed: {resp.status_code}")
    return resp.json()["bucket"]


def sanitize(input: str) -> str:
    """Normalize wiki strings: strip link/file markup, replace spaces with underscores."""
    return (
        input.replace("[[", "").replace("]]", "").replace(" ", "_").replace("File:", "")
    )


def item(item_name: str) -> Dict[str, str] | None:
    """
    Resolve an item to its wiki page and image.

    Tries 'infobox_item' with default_version=true. Falls back to a non-default_version query
    if no default exists. Returns the first match.

    Args:
        item_name: Item display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} or None if not found.
    """
    bucket = bucket_query("infobox_item", item_name)
    if not bucket:
        # some items don't have a default version, and all share same image
        bucket = bucket_query("infobox_item2", item_name)
    if not bucket:
        return None
    page_name: str = sanitize(bucket[0]["page_name"])
    image_file: str = sanitize(bucket[0]["image"][0])
    wiki_url = BASE + "w/" + page_name
    image_url = BASE + "images/" + image_file
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def spell(spell_name: str) -> Dict[str, str] | None:
    """
    Resolve a spell to its wiki page and image.

    Args:
        spell_name: Spell display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} or None if not found.
    """
    spell_name = spell_name.strip()
    bucket = bucket_query("infobox_spell", spell_name)
    if not bucket:
        return None
    page_name: str = sanitize(bucket[0]["page_name"])
    image_file: str = sanitize(bucket[0]["image"])
    wiki_url = BASE + "w/" + page_name
    image_url = BASE + "images/" + image_file
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def construction(object_name: str) -> dict | None:
    """
    Resolve a Construction object to its wiki page and icon.

    Uses default_version=true. If not found, retries with ' (construction)' suffix.

    Args:
        object_name: Object display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} or None if not found.
    """
    object_name = object_name.strip()
    bucket = bucket_query("infobox_construction", object_name)
    if not bucket:
        bucket = bucket_query("infobox_construction", object_name + " (construction)")
    if not bucket:
        return None
    page_name: str = sanitize(bucket[0]["page_name"])
    image_file: str = sanitize(bucket[0]["icon"][0])
    wiki_url = BASE + "w/" + page_name
    image_url = BASE + "images/" + image_file
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def quest(quest_name: str) -> Dict[str, str] | None:
    """
    Resolve a quest to its wiki page. Uses a fixed quest point icon.

    Args:
        quest_name: Quest display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} or None if not found.
    """
    quest_name = quest_name.strip()
    bucket = bucket_query("quest", quest_name)
    if not bucket:
        return None
    page_name: str = sanitize(bucket[0]["page_name"])
    wiki_url = BASE + "w/" + page_name
    image_url = BASE + "images/Quest_point_icon.png"
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def skill(skill_name: str) -> Dict[str, str] | None:
    """
    Resolve a skill to its wiki page and icon.

    Normalizes 'Runecrafting' -> 'Runecraft'. Validates against known skills.

    Args:
        skill_name: Skill display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} or None if not found/invalid.
    """
    # runecrafting is colloquially so well established some might get confused its actually called Runecraft.
    skill_name = skill_name.capitalize().strip()
    if skill_name == "Runecrafting":
        skill_name = "Runecraft"
    if skill_name not in SKILLS:
        return None
    wiki_url = f"https://oldschool.runescape.wiki/w/{skill_name}"
    image_url = BASE + "images/" + skill_name + "_icon.png"
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def generalized_search(search: str) -> Dict[str, str] | None:
    """ask osrs wiki api for wiki_url on anything. does not ask for img_url"""
    query = {
        "action": "opensearch",
        "format": "json",
        "formatversion": 2,
        "search": search,
        "redirects": "resolve",
    }
    print("generalized search occured")
    resp = s.get("https://oldschool.runescape.wiki/api.php", params=query)
    wiki_url = resp.json()[3][0]
    image_url = BASE + "images/Null.png"
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def slayer_rewards(reward_name: str) -> Dict[str, str] | None:
    """
    Resolve a Slayer reward to its wiki page and image using a local CSV.

    Args:
        reward_name: Reward display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} or None if not found.
    """
    reward_name = reward_name.lower().strip()
    df = pd.read_csv(SLAYER_REWARDS_CSV)
    df["unlock_name_lowercase"] = df["unlock_name"].map(lambda text: text.lower())
    try:
        image_file = (
            df.loc[df["unlock_name_lowercase"] == reward_name, "filename"]
            .item()
            .replace(" ", "_")
        )
    except ValueError as e:
        return None
    wiki_url = BASE + "w/" + "Slayer_Rewards"
    image_url = BASE + "images/" + image_file
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def prayer(prayer_name: str) -> Dict[str, str] | None:
    """
    Resolve a prayer to its wiki page and image using a local CSV.

    Args:
        prayer_name: Prayer display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} or None if not found.
    """
    prayer_name = prayer_name.lower().strip()
    df = pd.read_csv(PRAYERS_CSV)
    df["name_lowercase"] = df["name"].map(lambda text: text.lower())
    try:
        image_file = df.loc[df["name_lowercase"] == prayer_name, "filename"].item()
        page_name = (
            df.loc[df["name_lowercase"] == prayer_name, "name"].item().replace(" ", "_")
        )
    except ValueError:
        return None
    wiki_url = BASE + "w/" + page_name
    image_url = BASE + "images/" + image_file
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def search_all(input: str) -> Dict[str, str] | None:
    """
    Try all resolvers in order; return the first match.

    Order: item → spell → construction → skill → quest → prayer → slayer_rewards → generalized_search.

    Args:
        input: Display name or query.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} or None if all resolvers fail.
    """
    fns = [
        item,
        spell,
        construction,
        skill,
        quest,
        prayer,
        slayer_rewards,
        generalized_search,
    ]
    for fn in fns:
        result = fn(input)
        if result:
            return result
    return None


if __name__ == "__main__":
    spell("ice barrage")
    pass
