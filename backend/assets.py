"""Fetch and serve assets at runtime to the frontend server."""

from pathlib import Path

from dotenv import load_dotenv

from shared.id_asset import IdAsset
from shared.manual_asset import ManualAsset

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "data/chartbuilder-assets"
load_dotenv(ROOT_DIR / ".env")


def item_icon_path(milestone: str) -> tuple[Path, str]:
    """Fetch asset if applicable and return path.

    Args:
        milestone: user-submitted milestone to fetch.

    Returns:
        Milestone icon path and milestone name with correct capitalization.

    Raises:
        ValueError: milestone not found in names.json.
    """
    try:
        obj = IdAsset(milestone, asset_dir=ASSETS_DIR)
        if not obj.path.exists():
            obj.get_asset()
        correct_caps = obj.milestone_correct_caps
    except ValueError:
        try:
            obj = ManualAsset(milestone)
            correct_caps = obj.milestone
        except FileNotFoundError:
            raise ValueError(
                "File could not be resolved by ID or manual asset resolvers."
            )
    return obj.path, correct_caps
