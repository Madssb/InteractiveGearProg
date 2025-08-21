import re

import pytest
import requests
from requests.utils import quote

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


def item(item_name: str) -> dict:
    """ask osrs wiki api for wikiLink and imgSrc for item"""
    # default version handles wiki pages with
    params = {
        "action": "bucket",
        "format": "json",
        "query": f"bucket('infobox_item').select('page_name', 'image').where('page_name','{item_name}').where('default_version',true).run()",
    }
    resp = s.get("https://oldschool.runescape.wiki/api.php", params=params)
    if not resp.ok:
        raise ConnectionError(f"request failed: {resp.status_code}")
    if not resp.json()["bucket"]:
        return None  # no results
    page_name: str = resp.json()["bucket"][0]["page_name"].replace(" ", "_")
    image_file: str = resp.json()["bucket"][0]["image"][0].replace(" ", "_")

    wiki_url = f"https://oldschool.runescape.wiki/w/{page_name}"
    image_url = f"https://oldschool.runescape.wiki/w/{image_file}"
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def spell(spell_name: str) -> dict:
    """ask osrs wiki api for wikiLink and imgSrc for spell"""

    params = {
        "action": "bucket",
        "format": "json",
        "query": f"bucket('infobox_spell').select('page_name', 'image').where('page_name','{spell_name}').run()",
    }
    resp = s.get("https://oldschool.runescape.wiki/api.php", params=params)
    if not resp.ok:
        raise ConnectionError(f"request failed: {resp.status_code}")
    if not resp.json()["bucket"]:
        return None  # no results
    page_name: str = resp.json()["bucket"][0]["page_name"].replace(" ", "_")
    image_file: str = (
        resp.json()["bucket"][0]["image"]
        .replace(" ", "_")
        .replace("[[", "")
        .replace("]]", "")
    )
    wiki_url = f"https://oldschool.runescape.wiki/w/{page_name}"
    image_url = f"https://oldschool.runescape.wiki/w/{image_file}"
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def construction(input):
    """ask osrs wiki api for wikiLink and imgSrc for item"""
    params = {
        "action": "bucket",
        "format": "json",
        "query": f"bucket('infobox_construction').select('page_name', 'icon').where('page_name','{input}').run()",
    }
    resp = s.get("https://oldschool.runescape.wiki/api.php", params=params)
    if not resp.ok:
        raise ConnectionError(f"request failed: {resp.status_code}")
    if not resp.json()["bucket"]:
        return None  # no results
    page_name: str = resp.json()["bucket"][0]["page_name"].replace(" ", "_")
    image_file: str = resp.json()["bucket"][0]["icon"][0].replace(" ", "_")
    wiki_url = f"https://oldschool.runescape.wiki/w/{page_name}"
    image_url = f"https://oldschool.runescape.wiki/w/{image_file}"
    entry = {"wikiUrl": wiki_url, "imgUrl": image_url}
    return entry


def skill(skill_name: str):
    """ask osrs wiki api for wikiLink and imgSrc for skill."""
    # runecrafting is colloquially so well established some might get confused its actually called Runecraft.
    if skill_name.capitalize() == "Runecrafting":
        skill_name = "Runecraft"
    if skill_name.capitalize() not in SKILLS:
        return None
    wiki_url = f"https://oldschool.runescape.wiki/w/{skill_name.capitalize()}"
    image_url = (
        f"https://oldschool.runescape.wiki/w/File:{skill_name.capitalize()}_icon.png"
    )
    entry = {"wikiUrl": wiki_url, "imgUrl": image_url}
    return entry


def quest(quest_name: str):
    """ask osrs wiki api for wikiLink"""
    params = {
        "action": "bucket",
        "format": "json",
        "query": f"bucket('quest').select('page_name').where('page_name','{quest_name}').run()",
    }
    resp = s.get("https://oldschool.runescape.wiki/api.php", params=params)
    if not resp.ok:
        raise ConnectionError(f"request failed: {resp.status_code}")
    if not resp.json()["bucket"]:
        return None  # no results
    page_name: str = resp.json()["bucket"][0]["page_name"].replace(" ", "_")
    wiki_url = f"https://oldschool.runescape.wiki/w/{page_name}"
    image_url = f"https://oldschool.runescape.wiki/images/Quest_point_icon.png?dc356"
    entry = {"wikiUrl": wiki_url, "imgUrl": image_url}
    return entry


# def generalized_search(search: str):
#     """ask osrs wiki api for wiki_url on anything. does not ask for img_url"""
#     query = {
#         "action": "opensearch",
#         "format": "json",
#         "formatversion": 2,
#         "search": search,
#         "redirects": "resolve",
#     }
#     resp = s.get("https://oldschool.runescape.wiki/api.php", params=query)
#     wiki_url = resp.json()[3][0]
#     return wiki_url


def search_all(input: str):
    """accept just about anything"""
    input = input.replace("'", "\\'")  # handle cases like tumeken's shadow
    result = item(input)
    if result:
        return result
    result = spell(input)
    if result:
        return result
    result = construction(input)
    if result:
        return result
    result = skill(input)
    if result:
        return result
    result = quest(input)
    if result:
        return result
    return None


if __name__ == "__main__":
    print(quest("gertrude's cat"))
