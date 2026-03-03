# tests/test_query_wiki_api.py
import os

import pytest

pytestmark = pytest.mark.integration

if os.getenv("RUN_LIVE_TESTS") != "1":
    pytest.skip("Set RUN_LIVE_TESTS=1 to run live integration tests.", allow_module_level=True)

from osrswiki_images import search, search_many

# (name, wiki_url, image_url)
CASES = [
    (
        "abyssal whip",  # canonical item, no subpages
        "https://oldschool.runescape.wiki/w/Abyssal_whip",
        "https://oldschool.runescape.wiki/images/Abyssal_whip.png",
    ),
    (
        "trident of the swamp",  # has two subpages
        "https://oldschool.runescape.wiki/w/Trident_of_the_swamp",
        "https://oldschool.runescape.wiki/images/Trident_of_the_swamp.png",
    ),
    (
        "tumeken's shadow",  # has an apostrophe in page name.
        "https://oldschool.runescape.wiki/w/Tumeken's_shadow",
        "https://oldschool.runescape.wiki/images/Tumeken's_shadow.png",
    ),
    (
        "black mask (i)",  # no default version → fallback path
        "https://oldschool.runescape.wiki/w/Black_mask_(i)",
        "https://oldschool.runescape.wiki/images/Black_mask_(i).png",
    ),
    (
        "occult altar",
        "https://oldschool.runescape.wiki/w/Occult_altar",
        "https://oldschool.runescape.wiki/images/Occult_altar_icon.png",
    ),
    (
        "dark altar",  # suffix retry path
        "https://oldschool.runescape.wiki/w/Dark_altar_(Construction)",
        "https://oldschool.runescape.wiki/images/Dark_altar_(Construction)_icon.png",
    ),
    (
        "rejuvenation pool",  # multiple versions; one default
        "https://oldschool.runescape.wiki/w/Rejuvenation_pool",
        "https://oldschool.runescape.wiki/images/Rejuvenation_pool_icon.png",
    ),
    (
        "ice barrage",
        "https://oldschool.runescape.wiki/w/Ice_Barrage",
        "https://oldschool.runescape.wiki/images/Ice_Barrage.png",
    ),
    (
        "agility",
        "https://oldschool.runescape.wiki/w/Agility",
        "https://oldschool.runescape.wiki/images/Agility_icon.png",
    ),
    (
        "runecrafting",  # normalization to Runecraft
        "https://oldschool.runescape.wiki/w/Runecraft",
        "https://oldschool.runescape.wiki/images/Runecraft_icon.png",
    ),
    (
        "lost city",
        "https://oldschool.runescape.wiki/w/Lost_City",
        "https://oldschool.runescape.wiki/images/Quest_point_icon.png",
    ),
    (
        "bigger and badder",
        "https://oldschool.runescape.wiki/w/Slayer_Rewards",
        "https://oldschool.runescape.wiki/images/Bigger_and_Badder.png",
    ),
    (
        "protect from melee",
        "https://oldschool.runescape.wiki/w/Protect_from_Melee",
        "https://oldschool.runescape.wiki/images/Protect_from_Melee.png",
    ),
]


def _ids(data):
    return [t[0] for t in data]


def _check(result, wiki_url_truth, image_url_truth):
    assert result is not None, "resolver returned None"
    assert result["wikiUrl"] == wiki_url_truth
    assert result["imgUrl"] == image_url_truth


@pytest.mark.parametrize("name,wiki,img", CASES, ids=_ids(CASES))
def test_search(name, wiki, img):
    _check(search(name), wiki, img)


# Negative-path coverage
def test_unknown_returns_none():
    assert search("NotASkill") is None


def test_item_list_input():
    items = ["abyssal whip", "bandos godsword"]
    expected = {
        "abyssal whip": {
            "wikiUrl": "https://oldschool.runescape.wiki/w/Abyssal_whip",
            "imgUrl": "https://oldschool.runescape.wiki/images/Abyssal_whip.png",
            "type": "item",
        },
        "bandos godsword": {
            "wikiUrl": "https://oldschool.runescape.wiki/w/Bandos_godsword",
            "imgUrl": "https://oldschool.runescape.wiki/images/Bandos_godsword.png",
            "type": "item",
        },
    }
    result = search_many(items)
    assert result == expected


def test_item_list_input_keep_missing():
    items = ["abyssal whip", "this definitely does not exist 12345"]
    result = search_many(items, skip_missing=False)
    assert result["abyssal whip"]["wikiUrl"].endswith("/Abyssal_whip")
    assert result["this definitely does not exist 12345"] is None
