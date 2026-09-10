"""Asset management for milestones with an ingame item-ID.

Makes use of the static runelite GH repository.

Known quirks:
1. Items that can be noted appear to not have the noted icon occupy the lower item id
2. dt 2 rings lowest id match against assets not used ingame.
"""

import json
from pathlib import Path

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
NAMES_PATH = Path(ROOT_DIR / "data/cache/names.json")
NOTES_PATH = Path(ROOT_DIR / "data/cache/notes.json")
NAMES_VETTED_PATH = Path(ROOT_DIR / "data/cache/named_wiki_vetted.json")
OVERRIDES = {
    "Ultor ring": "28307",
    "Magus ring": "28313",
    "Venator ring": "28310",
    "Bellator ring": "28316",
    "Soulreaper axe": "28338",
}

s = requests.Session()
s.headers.update(
    {
        "user-agent": "Madlor (InteractiveGearProg) (https://github.com/Madssb/InteractiveGearProg)"
    }
)
with NAMES_PATH.open() as r:
    NAMES = json.load(r)
with NOTES_PATH.open() as r:
    NOTES = json.load(r)
series = pd.Series(data=NAMES)
series = series.str.lower()


class IdAsset:
    """Management of milestones identifiable by ingame item-Ids.

    Matches milestone to runelite cache json case-insensitively.

    Raises:
        TypeError: If neither or both of `milestone` and `item_id` are specified. Also raises if `milestone` is not str or `item_id` is not int.
    """

    def __init__(
        self, milestone: str | None = None, item_id: int | str | None = None
    ) -> None:
        """Instantiate self.milestone, self.item_id, ansd self.path

        Raises:
            TypeError: Raises this error if one of the following criterion are true:
                1. milestone and item_id both specified.
                2. neither of milestone and item_id are specified.
                2. milestone is not str.
                3. item_id is not str or int.
            ValueError: Raises this error if one of the following criterion are true:
                1. item_id couldn't be coerced via str(int(item_id)).
                2. item_id couldn't be found in names.json.

        """
        # reject both specified or neither specified
        if milestone is None and item_id is None:
            raise TypeError("Must specify one of milestone, item_id in constructor.")
        if milestone is not None and item_id is not None:
            raise TypeError("Must specify one of milestone, item_id in constructor.")

        # Require proper types
        if milestone is not None and not isinstance(milestone, str):
            raise TypeError("Expected str type for milestone, got: ", type(milestone))

        if item_id is not None and not isinstance(item_id, (str, int)):
            raise TypeError(
                "Expected int or str type for item_id, got: ", type(item_id)
            )

        # Require valid content
        if milestone == "":
            raise ValueError("milestone is not allowed to be empty.")

        if item_id == "":
            raise ValueError("item_id is not allowed to be empty.")

        # coerce into integer with no zero-padding
        if item_id is not None:
            try:
                item_id = str(int(item_id))
            except ValueError:
                raise ValueError(
                    "Couldn't coerce item_id into proper formatting: ", item_id
                )

        if milestone is not None:
            # get item_id
            self.milestone: str = milestone
            self.intelligent_resolver()
        if item_id is not None:
            self.item_id: str = item_id
            try:
                self.milestone = series.loc[str(self.item_id)]
            except IndexError:
                raise ValueError(
                    f"Ingame item ID {self.item_id} not found in names.json"
                )

        self.path: Path = Path(
            ROOT_DIR / f"frontend/public/images/item_icons/{self.item_id}.png"
        )
        self.type = ""
        self.wiki_url = None

    def intelligent_resolver(self):
        """Get Ingame item id

        Logic is as follows:
        1. if single item id from lookup on val, return that one.
        2. if more than one, pick the lowest.

        The above fails for Ultor Ring and Magus ring, thus manual overrides for these until i figure out
        how to properly address it.
        """
        if not self.milestone:
            raise ValueError("no milestone specified; nothing to resolve.")

        # Temporary measure while magus ring and ultor ring dont resolve properly.
        for ms, val in OVERRIDES.items():
            if self.milestone.lower() == ms.lower():
                self.item_id: str = val
                return

        item_ids = series.index[series == self.milestone.lower()].tolist()
        if item_ids == []:
            raise ValueError(f"milestone {self.milestone} not found in names.json")

        # 1 val = match to 1st index. 2 val = match to 1st index. >2, match to first also, but fails.
        self.item_id: str = str(item_ids[0])

    def __str__(self):
        return f"milestone: {self.milestone}\tid: {self.item_id}\tpath: {self.path}"

    def get_asset(self):
        """Gets milestone icon asset to disk from static runelite repo.

        Raises:
            FileExistsError: If asset already exists.
        """
        if self.path.exists():
            raise FileExistsError(f"{self.path} already exists.")
        download_url = f"https://raw.githubusercontent.com/runelite/static.runelite.net/gh-pages/cache/item/icon/{self.item_id}.png"
        res = s.get(download_url)
        res.raise_for_status()
        if res.status_code == 200:
            with open(self.path, "wb") as file:
                file.write(res.content)
            print(f"Wrote to disk: {self.path}")

    def all_item_ids(self) -> list[str]:
        """Get all item ids."""
        if not self.milestone:
            raise ValueError("no milestone specified; nothing to resolve.")
        return series.index[series == self.milestone.lower()].tolist()

    def asset_urls(self) -> list[str]:
        """Get all icon asset runelite source urls.

        Returns:
            list[str]: List of all urls.
        """
        all_ids = self.all_item_ids()
        urls: list[str] = []
        for item_id in all_ids:
            download_url = f"https://raw.githubusercontent.com/runelite/static.runelite.net/gh-pages/cache/item/icon/{item_id}.png"
            urls.append(download_url)
        return urls
