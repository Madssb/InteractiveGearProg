"""For docker image to catch missing files"""

# uv run --project backend python -m backend.tests.test_required_files_exist
from shared.paths import (
    CHANGELOG_PATH,
    MAIN_SEQUENCE_PATH,
    MILESTONE_IDS_PATH,
    MILESTONE_METADATA_PATH,
    NAMES_PATH,
    PRAYER_ICONS_DIR,
    RETIREMENT_SEQUENCE_PATH,
    SKILL_ICONS_DIR,
    SLAYER_ICONS_DIR,
    SPELL_ICONS_DIR,
)

paths = [
    MAIN_SEQUENCE_PATH,
    RETIREMENT_SEQUENCE_PATH,
    MILESTONE_IDS_PATH,
    MILESTONE_METADATA_PATH,
    CHANGELOG_PATH,
    NAMES_PATH,
    PRAYER_ICONS_DIR,
    SKILL_ICONS_DIR,
    SPELL_ICONS_DIR,
    SLAYER_ICONS_DIR,
]

for path in paths:
    assert path.exists(), f"Missing required file: {path}"
