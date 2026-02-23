from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Iterable, List, Set

from .client import search, search_many


def _flatten(xs: Any) -> Iterable[str]:
    """Yield strings from a possibly nested list/tuple structure."""
    if isinstance(xs, (list, tuple)):
        for x in xs:
            yield from _flatten(x)
    elif isinstance(xs, str):
        # only keep non-empty strings
        s = xs.strip()
        if s:
            yield s
    else:
        # ignore non-string scalars (numbers, bools, None)
        return


def _read_input(path: str) -> Any:
    if path == "-":
        text = sys.stdin.read()
    else:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    return json.loads(text)


def main() -> None:
    p = argparse.ArgumentParser(
        prog="osrswiki-images",
        description="Resolve OSRS names to {name: {wikiUrl, imgUrl}}.",
    )
    p.add_argument(
        "-i",
        "--input",
        default="-",
        help="Path to JSON (nested list of strings). Use '-' for stdin. "
        "If omitted and you pass positional names, the JSON is ignored.",
    )
    p.add_argument(
        "-o",
        "--output",
        default="-",
        help="Path to write JSON mapping. Use '-' for stdout (default).",
    )
    p.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Do not deduplicate names (default is to dedupe).",
    )
    p.add_argument(
        "--include-missing",
        action="store_true",
        help="Include names that failed to resolve with value null.",
    )
    p.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent (default 2; use 0 for compact).",
    )
    p.add_argument(
        "names",
        nargs="*",
        help='Optional positional names, e.g. `osrswiki-images "abyssal whip" "ice barrage"`',
    )
    args = p.parse_args()

    # Determine names source: positional args win; otherwise read JSON input
    if args.names:
        names_iter = (n for n in args.names if n.strip())
    else:
        try:
            data = _read_input(args.input)
        except Exception as e:
            sys.stderr.write(f"error: failed to read JSON from {args.input}: {e}\n")
            sys.exit(2)
        names_iter = _flatten(data)

    # Deduplicate while preserving order unless --no-dedupe
    if args.no_dedupe:
        names_list = [n for n in names_iter]
    else:
        seen: Set[str] = set()
        names_list: List[str] = []
        for n in names_iter:
            if n not in seen:
                seen.add(n)
                names_list.append(n)

    # Resolve
    mapping: Dict[str, Dict[str, str]] = search_many(
        names_list, skip_missing=not args.include_missing
    )

    # Write result
    text = json.dumps(mapping, ensure_ascii=False, indent=(args.indent or None))
    if args.output == "-":
        sys.stdout.write(text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
