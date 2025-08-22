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
BASE = "https://oldschool.runescape.wiki/w/"


def bucket_query(bucket_name: str, name: str):
    name = name.replace("'", "\\'")  # handle cases like tumeken's shadow
    query_string = {
        "infobox_item": f"bucket('infobox_item').select('page_name', 'image').where('page_name','{name}').where('default_version',true).run()",
        "infobox_spell": f"bucket('infobox_spell').select('page_name', 'image').where('page_name','{name}').run()",
        "infobox_construction": f"bucket('infobox_construction').select('page_name', 'icon').where('page_name','{name}').run()",
        "quest": f"bucket('quest').select('page_name').where('page_name','{name}').run()",
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


def item(item_name: str) -> dict | None:
    """ask osrs wiki api for wikiLink and imgSrc for item"""
    bucket = bucket_query("infobox_item", item_name)
    if not bucket:
        return None
    page_name: str = bucket[0]["page_name"].replace(" ", "_")
    image_file: str = bucket[0]["image"][0].replace(" ", "_")

    wiki_url = BASE + page_name
    image_url = BASE + image_file
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def spell(spell_name: str) -> dict | None:
    """ask osrs wiki api for wikiLink and imgSrc for spell"""
    bucket = bucket_query("infobox_spell", spell_name)
    if not bucket:
        return None
    page_name: str = bucket[0]["page_name"].replace(" ", "_")
    image_file: str = (
        bucket[0]["image"].replace(" ", "_").replace("[[", "").replace("]]", "")
    )
    wiki_url = BASE + page_name
    image_url = BASE + image_file
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def construction(name) -> dict | None:
    """ask osrs wiki api for wikiLink and imgSrc for construction object"""
    bucket = bucket_query("infobox_construction", name)
    if not bucket:
        return None
    page_name: str = bucket[0]["page_name"].replace(" ", "_")
    image_file: str = bucket[0]["icon"][0].replace(" ", "_")
    wiki_url = BASE + page_name
    image_url = BASE + image_file
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def quest(quest_name: str) -> dict | None:
    """ask osrs wiki api for wikiLink"""
    bucket = bucket_query("quest", quest_name)
    if not bucket:
        return None
    page_name: str = bucket[0]["page_name"].replace(" ", "_")
    wiki_url = BASE + page_name
    image_url = BASE + "images/Quest_point_icon.png"
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def skill(skill_name: str) -> dict | None:
    """ask osrs wiki api for wikiLink and imgSrc for skill."""
    # runecrafting is colloquially so well established some might get confused its actually called Runecraft.
    skill_name = skill_name.capitalize()
    if skill_name == "Runecrafting":
        skill_name = "Runecraft"
    if skill_name not in SKILLS:
        return None
    wiki_url = f"https://oldschool.runescape.wiki/w/{skill_name}"
    image_url = BASE + "File:" + skill_name + "_icon.png"
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def generalized_search(search: str) -> dict | None:
    """ask osrs wiki api for wiki_url on anything. does not ask for img_url"""
    query = {
        "action": "opensearch",
        "format": "json",
        "formatversion": 2,
        "search": search,
        "redirects": "resolve",
    }
    resp = s.get("https://oldschool.runescape.wiki/api.php", params=query)
    wiki_url = resp.json()[3][0]
    image_url = BASE + "File:Null.png"
    return {"wikiUrl": wiki_url, "imgUrl": image_url}


def slayer_rewards(name: str):
    name = name.lower()

    df = pd.read_csv("data/slayer_rewards.csv")
    df["unlock_name"] = df["unlock_name"].map(lambda text: text.lower())
    try:
        image_file = (
            df.loc[df["unlock_name"] == name, "filename"].item().replace(" ", "_")
        )
    except ValueError:
        return None
    image_url = BASE + image_file
    wiki_url = BASE + "Slayer_Rewards"
    return {"wikiUrl": wiki_url, "imageUrl": image_url}


def search_all(input: str) -> dict | None:
    """iteratively attempt all queries with input, returning appropriate one or none"""
    fns = [item, spell, construction, skill, quest, generalized_search]
    for fn in fns:
        result = fn(input)
        if result:
            return result
    return None


if __name__ == "__main__":
    # print(search_all("auto-weed"))
    print(slayer_rewards("get smashed"))
