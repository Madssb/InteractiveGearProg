"""
osrswiki_images
===============

Public API
----------
- search(name): resolve a single OSRS name to {'wikiUrl','imgUrl'} or None
- search_many(names, *, skip_missing=True): batch resolve into {name: {...}}

Notes
-----
All other functions are internal helpers and may change without notice.
"""

from .client import item_rs3, search, search_many

__all__ = ["search", "search_many", "item_rs3"]
