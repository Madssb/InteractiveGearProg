"""Project paths.

Makes testing docker container simpler and helps mitigate code duplication.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

MAIN_SEQUENCE_PATH = ROOT_DIR / "data/logic/milestone-sequence-main.json"
RETIREMENT_SEQUENCE_PATH = ROOT_DIR / "data/logic/milestone-sequence-retirement.json"
MILESTONE_METADATA_PATH = ROOT_DIR / "data/generated/milestone-metadata.json"
MILESTONE_IDS_PATH = ROOT_DIR / "data/logic/milestone-ids.json"
NAMES_PATH = ROOT_DIR / "data/cache/names.json"
NOTES_PATH = ROOT_DIR / "data/cache/notes.json"
CHANGELOG_PATH = ROOT_DIR / "data/contents/changelog.json"

IMAGES_DIR = Path(ROOT_DIR / "frontend/public")

ASSETS_DIR = ROOT_DIR / "data/chartbuilder-assets"

ITEMS_ICON_DIR = ROOT_DIR / "frontend/public/images/item_icons"

PRAYER_ICONS_DIR = Path(ROOT_DIR / "frontend/public/images/prayer_icons")
SKILL_ICONS_DIR = Path(ROOT_DIR / "frontend/public/images/skill_icons")
SPELL_ICONS_DIR = Path(ROOT_DIR / "frontend/public/images/spell_icons")
SLAYER_ICONS_DIR = Path(ROOT_DIR / "frontend/public/images/slayer_icons")

ENV_PATH = Path(ROOT_DIR / ".env")
