"""Asset management for milestones absent of automation for fetching assets."""

import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PRAYER_ICONS_DIR = Path(ROOT_DIR / "frontend/public/images/prayer_icons")
SKILL_ICONS_DIR = Path(ROOT_DIR / "frontend/public/images/skill_icons")
SPELL_ICONS_DIR = Path(ROOT_DIR / "frontend/public/images/spell_icons")
SLAYER_ICONS_DIR = Path(ROOT_DIR / "frontend/public/images/slayer_icons")
LVL_PAT = re.compile(r"\d{1,2} (\w+)")
SLAYER_KEYVALS = {
    "Bigger_and_Badder.webp": "Bigger and Badder",
    "Broad_arrowheads_5.webp": "Broader Fletching",
    "Lizardmen_icon.png": "Reptile got Ripped",
}


class ManualAsset:
    """Asset management For milestones with assets manually downloaded."""

    def __init__(self, milestone: str):
        """Instantiates self.milestone and self.path.

        Raises:
            TypeError: Milestone is not str
            ValueError: Milestone matches skill pattern, but no skill name.
            FileNotFoundError: Asset not found for specified milestone.
        """
        if not isinstance(milestone, str):
            raise TypeError(f"Invalid type on milestone. Expected str, got {type}.")
        self.milestone = milestone
        self._resolve_path()

    def _skill_icon_path(self) -> Path | None:
        """match milestone with skill icon path if applicable."""
        match = LVL_PAT.match(self.milestone)
        if match:
            for path in list(SKILL_ICONS_DIR.glob("*")):
                template = path.with_suffix("").name.replace("_icon", "").lower()
                if self.milestone.split(" ")[1].lower() == template:
                    return path
            raise ValueError(
                f"Milestone matches level pattern without a valid skill: {self.milestone}"
            )

    def _prayer_icon_path(self) -> Path | None:
        """Match milestone with prayer icon path if applicable."""
        for path in list(PRAYER_ICONS_DIR.glob("*")):
            template = path.with_suffix("").name.lower().replace("_", " ")
            if self.milestone.lower() == template:
                return path

    def _magic_icon_path(self) -> Path | None:
        """Match milestone with spell icon path if applicable."""
        for path in list(SPELL_ICONS_DIR.glob("*")):
            template = path.with_suffix("").name.lower().replace("_", " ")
            if self.milestone.lower() == template:
                return path

    def _slayer_icon_path(self) -> Path | None:
        """Match milestone with slayer icon path if applicable"""
        for path in list(SLAYER_ICONS_DIR.glob("*")):
            template = path.with_suffix("").name.lower().replace("_", " ")
            if self.milestone.lower() == template:
                return path

    def _resolve_path(self):
        """Path resolver that exits early on completion.

        Raises:

        """
        methods = [
            self._skill_icon_path,
            self._prayer_icon_path,
            self._magic_icon_path,
            self._slayer_icon_path,
        ]
        for method in methods:
            path = method()
            if path:
                self.path = path
                return
        raise FileNotFoundError(f"Couldnt match {self.milestone} to an icon path.")

    def __str__(self):
        return f"milestone: {self.milestone}, path: {self.path}"
