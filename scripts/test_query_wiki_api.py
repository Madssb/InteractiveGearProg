import pytest
from query_wiki_api import construction, item, quest, search_all, skill, spell

# (item name, wiki_url, image_url)
testdata_item = [
    (
        "abyssal whip",
        "https://oldschool.runescape.wiki/w/Abyssal_whip",
        "https://oldschool.runescape.wiki/w/File:Abyssal_whip.png",
    ),
    (
        "trident of the swamp",
        "https://oldschool.runescape.wiki/w/Trident_of_the_swamp",
        "https://oldschool.runescape.wiki/w/File:Trident_of_the_swamp.png",
    ),
    (
        "amulet of glory",
        "https://oldschool.runescape.wiki/w/Amulet_of_glory",
        "https://oldschool.runescape.wiki/w/File:Amulet_of_glory(4).png",
    ),
    (
        "ring of dueling",
        "https://oldschool.runescape.wiki/w/Ring_of_dueling",
        "https://oldschool.runescape.wiki/w/File:Ring_of_dueling(8).png",
    ),
    (
        "games necklace",
        "https://oldschool.runescape.wiki/w/Games_necklace",
        "https://oldschool.runescape.wiki/w/File:Games_necklace(8).png",
    ),
    (
        "combat bracelet",
        "https://oldschool.runescape.wiki/w/Combat_bracelet",
        "https://oldschool.runescape.wiki/w/File:Combat_bracelet.png",
    ),
    (
        "tumeken's shadow",
        "https://oldschool.runescape.wiki/w/Tumeken's_shadow",
        "https://oldschool.runescape.wiki/w/File:Tumeken's_shadow.png",
    ),
]


testdata_construction = [
    (
        "occult altar",
        "https://oldschool.runescape.wiki/w/Occult_altar",
        "https://oldschool.runescape.wiki/w/File:Occult_altar_icon.png",
    ),
    (
        "dark altar (construction)",
        "https://oldschool.runescape.wiki/w/Dark_altar_(Construction)",
        "https://oldschool.runescape.wiki/w/File:Dark_altar_(Construction)_icon.png",
    ),
]


testdata_spell = [
    (
        "ice barrage",
        "https://oldschool.runescape.wiki/w/Ice_Barrage",
        "https://oldschool.runescape.wiki/w/File:Ice_Barrage.png",
    ),
    (
        "vengeance",
        "https://oldschool.runescape.wiki/w/Vengeance",
        "https://oldschool.runescape.wiki/w/File:Vengeance.png",
    ),
    (
        "resurrect greater ghost",
        "https://oldschool.runescape.wiki/w/Resurrect_Greater_Ghost",
        "https://oldschool.runescape.wiki/w/File:Resurrect_Greater_Ghost.png",
    ),
]


testdata_skill = [
    (
        "agility",
        "https://oldschool.runescape.wiki/w/Agility",
        "https://oldschool.runescape.wiki/w/File:Agility_icon.png",
    ),
    (
        "runecrafting",
        "https://oldschool.runescape.wiki/w/Runecraft",
        "https://oldschool.runescape.wiki/w/File:Runecraft_icon.png",
    ),
]


testdata_quest = [
    (
        "icthlarin's little helper",
        "https://oldschool.runescape.wiki/w/Icthlarin's_Little_Helper",
        "https://oldschool.runescape.wiki/images/Quest_point_icon.png?dc356",
    ),
    (
        "lost city",
        "https://oldschool.runescape.wiki/w/Lost_City",
        "https://oldschool.runescape.wiki/images/Quest_point_icon.png?dc356",
    ),
]


testdata_all = (
    testdata_item
    + testdata_construction
    + testdata_spell
    + testdata_skill
    + testdata_quest
)
for elem in testdata_all:
    print(elem)


# @pytest.mark.parametrize("item_name,wiki_url_truth,image_url_truth", testdata_item)
# def test_item(item_name, wiki_url_truth, image_url_truth):
#     result = item(item_name)
#     if result["wikiUrl"] != wiki_url_truth:
#         raise AssertionError(
#             "expected:",
#             wiki_url_truth,
#             ", got:",
#             result["wikiUrl"],
#         )
#     if result["imgUrl"] != image_url_truth:
#         raise AssertionError(
#             "expected:",
#             image_url_truth,
#             ", got:",
#             result["imgUrl"],
#         )


# @pytest.mark.parametrize(
#     "item_name,wiki_url_truth,image_url_truth", testdata_construction
# )
# def test_construction(item_name, wiki_url_truth, image_url_truth):
#     result = construction(item_name)
#     if result["wikiUrl"] != wiki_url_truth:
#         raise AssertionError(
#             "expected:",
#             wiki_url_truth,
#             ", got:",
#             result["wikiUrl"],
#         )
#     if result["imgUrl"] != image_url_truth:
#         raise AssertionError(
#             "expected:",
#             image_url_truth,
#             ", got:",
#             result["imgUrl"],
#         )


# @pytest.mark.parametrize("item_name,wiki_url_truth,image_url_truth", testdata_spell)
# def test_spell(item_name, wiki_url_truth, image_url_truth):
#     result = spell(item_name)
#     if result["wikiUrl"] != wiki_url_truth:
#         raise AssertionError(
#             "expected:",
#             wiki_url_truth,
#             ", got:",
#             result["wikiUrl"],
#         )
#     if result["imgUrl"] != image_url_truth:
#         raise AssertionError(
#             "expected:",
#             image_url_truth,
#             ", got:",
#             result["imgUrl"],
#         )


# @pytest.mark.parametrize("item_name,wiki_url_truth,image_url_truth", testdata_skill)
# def test_skill(item_name, wiki_url_truth, image_url_truth):
#     result = skill(item_name)
#     if result["wikiUrl"] != wiki_url_truth:
#         raise AssertionError(
#             "expected:",
#             wiki_url_truth,
#             ", got:",
#             result["wikiUrl"],
#         )
#     if result["imgUrl"] != image_url_truth:
#         raise AssertionError(
#             "expected:",
#             image_url_truth,
#             ", got:",
#             result["imgUrl"],
#         )


# @pytest.mark.parametrize("item_name,wiki_url_truth,image_url_truth", testdata_quest)
# def test_quest(item_name, wiki_url_truth, image_url_truth):
#     result = quest(item_name)
#     if result["wikiUrl"] != wiki_url_truth:
#         raise AssertionError(
#             "expected:",
#             wiki_url_truth,
#             ", got:",
#             result["wikiUrl"],
#         )
#     if result["imgUrl"] != image_url_truth:
#         raise AssertionError(
#             "expected:",
#             image_url_truth,
#             ", got:",
#             result["imgUrl"],
#         )


@pytest.mark.parametrize("item_name,wiki_url_truth,image_url_truth", testdata_all)
def test_search_all(item_name, wiki_url_truth, image_url_truth):
    result = search_all(item_name)
    if result["wikiUrl"] != wiki_url_truth:
        raise AssertionError(
            "expected:",
            wiki_url_truth,
            ", got:",
            result["wikiUrl"],
        )
    if result["imgUrl"] != image_url_truth:
        raise AssertionError(
            "expected:",
            image_url_truth,
            ", got:",
            result["imgUrl"],
        )
