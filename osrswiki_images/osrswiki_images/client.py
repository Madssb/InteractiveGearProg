"""
OSRS Wiki resolvers: map game entities to wiki and image URLs.

Network I/O
-----------
- Uses the OSRS Wiki API (`action=bucket` and `action=opensearch`) via a shared
  `requests.Session` with a fixed User-Agent.
- Low-level access: `_bucket_query(bucket_name, page_name)`.

Selection and Filtering
-----------------------
- Always selects 'page_name' and one media field.
- Media field: 'icon' for 'infobox_construction'; 'image' for other buckets.
- Applies `default_version=true` where supported; falls back for items without a
  default version.
- Page matching is case-insensitive; apostrophes in input are escaped.

Local Data
----------
- Packaged CSVs (`data/prayers.csv`, `data/slayer_rewards.csv`) provide filename
  mappings for `_prayer()` and `_slayer_rewards()`.

Return Conventions
------------------
- Public functions return `{'wikiUrl': str, 'imgUrl': str}` or `None`.
- `_bucket_query` returns a `List[Dict[str, str]]` (raw API records) or raises.
- Exceptions: `ConnectionError` on HTTP failure; `KeyError` for unknown bucket.

Public API
----------
- search(name): resolve a single name via all resolvers in order.
- search_many(names, *, skip_missing=True): batch resolve multiple names.

Internal Helpers (subject to change)
------------------------------------
- _item(name), _spell(name), _construction(name), _quest(name),
  _skill(name), _prayer(name), _slayer_rewards(name), _generalized_search(query).
"""

from __future__ import annotations

import time
from importlib.resources import files
from typing import Dict, Iterable, List, Optional

import backoff
import pandas as pd
import requests

BASE = "https://oldschool.runescape.wiki/"
API = "https://oldschool.runescape.wiki/api.php"
TIMEOUT = 8


class RetryableHTTPError(requests.exceptions.HTTPError): ...


class NonRetryableHTTPError(requests.exceptions.HTTPError): ...


s = requests.Session()
s.headers.update(
    {"user-agent": "osrswiki_images/v0.1 (https://github.com/Madssb/osrswiki_images)"}
)

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


def _pkg_csv_path(name: str) -> str:
    # packaged CSVs live at osrswiki_images/data/*.csv
    return str(files("osrswiki_images").joinpath("data", name))


def _raise_for_policy(resp: requests.Response) -> None:
    sc = resp.status_code
    if sc == 429 or 500 <= sc < 600:
        ra = resp.headers.get("Retry-After")
        if ra:
            try:
                time.sleep(int(ra))
            except ValueError:
                pass
        raise RetryableHTTPError(f"{sc}", response=resp)
    if sc >= 400:
        raise NonRetryableHTTPError(f"{sc}", response=resp)


@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=(
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        RetryableHTTPError,
    ),
    jitter=backoff.full_jitter,
    max_time=30,
    giveup=lambda e: isinstance(e, NonRetryableHTTPError),
)
def _get_with_backoff(params: Dict[str, str]) -> requests.Response:
    resp = s.get(API, params=params, timeout=TIMEOUT)
    _raise_for_policy(resp)
    return resp


def _bucket_query(bucket_name: str, page_name: str) -> List[Dict[str, str]]:
    """Fetch raw records from the OSRS Wiki bucket API.

    Selects 'page_name' and one media field based on the bucket:
    - items/spells → 'image'
    - construction → 'icon'
    Applies `default_version=true` where supported and escapes apostrophes in `page_name`.

    Args:
        bucket_name: One of {'infobox_item','infobox_item2','infobox_spell','infobox_construction','quest'}.
        page_name: Case-insensitive page name to match in the bucket.

    Returns:
        A list of raw record dicts from the 'bucket' JSON array.

    Raises:
        ConnectionError: HTTP error from the wiki API.
        KeyError: If an unknown bucket_name is provided.
    """
    page_name = page_name.replace("'", "\\'")  # handle e.g. tumeken's shadow
    q = {
        "infobox_item": f"bucket('infobox_item').select('page_name','image').where('page_name','{page_name}').where('default_version',true).run()",
        "infobox_item2": f"bucket('infobox_item').select('page_name','image').where('page_name','{page_name}').run()",
        "infobox_spell": f"bucket('infobox_spell').select('page_name','image').where('page_name','{page_name}').run()",
        "infobox_construction": f"bucket('infobox_construction').select('page_name','icon').where('page_name','{page_name}').where('default_version',true).run()",
        "quest": f"bucket('quest').select('page_name').where('page_name','{page_name}').run()",
    }
    params = {"action": "bucket", "format": "json", "query": q[bucket_name]}
    resp = _get_with_backoff(params)

    if not resp.ok:
        raise ConnectionError(f"request failed: {resp.status_code}")

    data = resp.json()
    if "bucket" not in data or not isinstance(data["bucket"], list):
        raise ConnectionError("malformed response: missing 'bucket'")

    return data["bucket"]


def _sanitize(text: str) -> str:
    """Normalize wiki strings for URLs.

    Removes wiki/file markup and replaces spaces with underscores.

    Args:
        text: A wiki page or filename string, possibly with markup.

    Returns:
        A sanitized string safe to append into wiki/image URLs.
    """
    return (
        text.replace("[[", "").replace("]]", "").replace(" ", "_").replace("File:", "")
    )


def _item(item_name: str) -> Dict[str, str] | None:
    """Resolve an item to its wiki page and image.

    Tries 'infobox_item' with default_version=true; falls back to 'infobox_item2'
    for items without a default version. Returns the first match.

    Args:
        item_name: Item display name (case-insensitive).

    Returns:
        {'wikiUrl': str, 'imgUrl': str} if found, else None.
    """
    bucket = _bucket_query("infobox_item", item_name)
    if not bucket:
        bucket = _bucket_query("infobox_item2", item_name)  # some items have no default
    if not bucket:
        return None
    page_name = _sanitize(bucket[0]["page_name"])
    image_file = _sanitize(bucket[0]["image"][0])
    return {
        "wikiUrl": f"{BASE}w/{page_name}",
        "imgUrl": f"{BASE}images/{image_file}",
        "type": "item",
    }


def _spell(spell_name: str) -> Dict[str, str] | None:
    """Resolve a spell to its wiki page and image.

    Args:
        spell_name: Spell display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} if found, else None.
    """
    spell_name = spell_name.strip()
    bucket = _bucket_query("infobox_spell", spell_name)
    if not bucket:
        return None
    page_name = _sanitize(bucket[0]["page_name"])
    image_file = _sanitize(bucket[0]["image"])
    return {
        "wikiUrl": f"{BASE}w/{page_name}",
        "imgUrl": f"{BASE}images/{image_file}",
        "type": "spell",
    }


def _construction(object_name: str) -> Dict[str, str] | None:
    """Resolve a Construction object to its wiki page and icon.

    Uses default_version=true; if not found, retries with ' (construction)' suffix.

    Args:
        object_name: Construction object display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} if found, else None.
    """
    n = object_name.strip()
    bucket = _bucket_query("infobox_construction", n)
    if not bucket:
        bucket = _bucket_query("infobox_construction", f"{n} (construction)")
    if not bucket:
        return None
    page_name = _sanitize(bucket[0]["page_name"])
    icon_file = _sanitize(bucket[0]["icon"][0])
    return {
        "wikiUrl": f"{BASE}w/{page_name}",
        "imgUrl": f"{BASE}images/{icon_file}",
        "type": "construction",
    }


def _quest(quest_name: str) -> Dict[str, str] | None:
    """Resolve a quest to its wiki page and a fixed quest point icon.

    Args:
        quest_name: Quest display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} if found, else None.
    """
    q = quest_name.strip()
    bucket = _bucket_query("quest", q)
    if not bucket:
        return None
    page_name = _sanitize(bucket[0]["page_name"])
    return {
        "wikiUrl": f"{BASE}w/{page_name}",
        "imgUrl": f"{BASE}images/Quest_point_icon.png",
        "type": "quest",
    }


def _skill(skill_name: str) -> Dict[str, str] | None:
    """Resolve a skill to its wiki page and icon.

    Normalizes 'Runecrafting' → 'Runecraft' and validates against known skills.

    Args:
        skill_name: Skill display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} if valid, else None.
    """
    name = skill_name.capitalize().strip()
    if name == "Runecrafting":
        name = "Runecraft"
    if name not in SKILLS:
        return None
    return {
        "wikiUrl": f"{BASE}w/{name}",
        "imgUrl": f"{BASE}images/{name}_icon.png",
        "type": "skill",
    }


def _generalized_search(search: str) -> Dict[str, str] | None:
    """Fallback resolver using the OSRS Wiki OpenSearch endpoint.

    Useful for entities not covered by bucket queries. Does not resolve an image,
    returns a placeholder 'Null.png' image URL.

    Args:
        search: Free-text query.

    Returns:
        {'wikiUrl': str, 'imgUrl': '.../Null.png'} if any result, else None.
    """
    params = {
        "action": "opensearch",
        "format": "json",
        "formatversion": 2,
        "search": search,
        "redirects": "resolve",
    }
    # Keep the original side-effect for parity
    resp = _get_with_backoff(params)
    data = resp.json()
    if not data or not data[3]:
        return None
    return {"wikiUrl": data[3][0], "imgUrl": f"{BASE}images/Null.png", "type": "fail"}


def _slayer_rewards(reward_name: str) -> Dict[str, str] | None:
    """Resolve a Slayer reward to its wiki page and image using packaged CSV.

    Looks up `unlock_name` → icon filename mapping from `data/slayer_rewards.csv`.

    Args:
        reward_name: Slayer reward display name.

    Returns:
        {'wikiUrl': '.../Slayer_Rewards', 'imgUrl': str} if found, else None.
    """
    df = pd.read_csv(_pkg_csv_path("slayer_rewards.csv"))
    key = reward_name.lower().strip()
    df["unlock_name_lowercase"] = df["unlock_name"].map(lambda t: t.lower())
    try:
        image_file = (
            df.loc[df["unlock_name_lowercase"] == key, "filename"]
            .item()
            .replace(" ", "_")
        )
    except ValueError:
        return None
    return {
        "wikiUrl": f"{BASE}w/Slayer_Rewards",
        "imgUrl": f"{BASE}images/{image_file}",
        "type": "slayer",
    }


def _prayer(prayer_name: str) -> Dict[str, str] | None:
    """Resolve a prayer to its wiki page and image using packaged CSV.

    Looks up `name` → icon filename mapping from `data/prayers.csv`.

    Args:
        prayer_name: Prayer display name.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} if found, else None.
    """
    df = pd.read_csv(_pkg_csv_path("prayers.csv"))
    key = prayer_name.lower().strip()
    df["name_lowercase"] = df["name"].map(lambda t: t.lower())
    try:
        image_file = df.loc[df["name_lowercase"] == key, "filename"].item()
        page_name = df.loc[df["name_lowercase"] == key, "name"].item().replace(" ", "_")
    except ValueError:
        return None
    return {
        "wikiUrl": f"{BASE}w/{page_name}",
        "imgUrl": f"{BASE}images/{image_file}",
        "type": "prayer",
    }


def search(name: str) -> Dict[str, str] | None:
    """Try all resolvers in order and return the first match.

    Order:
        item → spell → construction → skill → quest → prayer → slayer_rewards → generalized_search.

    Args:
        input: Display name or free-text query.

    Returns:
        {'wikiUrl': str, 'imgUrl': str} or None if all resolvers fail.
    """
    for fn in (
        _item,
        _spell,
        _construction,
        _skill,
        _quest,
        _prayer,
        _slayer_rewards,
        _generalized_search,
    ):
        r = fn(name)
        if r:
            return r
    return None


def search_many(
    names: Iterable[str], *, skip_missing: bool = True
) -> Dict[str, Dict[str, str]]:
    """Batch resolve names.

    Args:
        names: strings to resolve
        skip_missing: if True, omit misses; if False, include with value None
    """
    out: Dict[str, Dict[str, str]] = {}
    for n in names:
        res = search(n)
        if res is not None:
            out[n] = res
        elif not skip_missing:
            out[n] = None  # type: ignore[assignment]
    return out


def item_rs3(item_name: str) -> Dict[str, str] | None:
    """Resolve an item to its wiki page and image.

    Tries 'infobox_item' with default_version=true; falls back to 'infobox_item2'
    for items without a default version. Returns the first match.

    Args:
        item_name: Item display name (case-insensitive).

    Returns:
        {'wikiUrl': str, 'imgUrl': str} if found, else None.
    """
    bucket = _bucket_query("infobox_item", item_name)
    if not bucket:
        bucket = _bucket_query("infobox_item2", item_name)  # some items have no default
    if not bucket:
        return None
    page_name = _sanitize(bucket[0]["page_name"])
    image_file = _sanitize(bucket[0]["image"][0])
    return {
        "wikiUrl": f"https://runescape.wiki/w/{page_name}",
        "imgUrl": f"https://runescape.wiki/images/{image_file}",
        "type": "item",
    }
