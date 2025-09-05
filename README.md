# Interactive OSRS Progression Chart — Minimal Template

This branch is a **starter** you can clone or fork to publish your own chart with zero build tooling. It renders a progression sequence from two JSON files:

- `data/sequence.json` — the order of items/skills to show (grouped in rows).
- `data/generated/items.json` — per-item `wikiUrl` and `imgUrl` (generated via Python).

No frameworks. Static HTML/CSS/JS only.

## Quick start

1. Fork or download this branch.
2. Edit `data/sequence.json` to list what you want rendered.
3. Generate `data/generated/items.json`:

   # requires Python 3.10+ and internet access to the OSRS Wiki

   python tools/build_items_json.py

   This script resolves every item in `sequence.json` using the OSRS Wiki API and bumps `data/generated/version.json` (used for cache invalidation).

4. Open `index.html` in a browser.

## What you can edit

- `data/sequence.json`

  Example structure (each inner array is a row/group):

      [
        ["Amulet of strength", "Climbing boots"],
        ["Rune pouch"],
        ["Dragon scimitar", "Berserker ring (i)"]
      ]

- `styles/styles.css` — layout/spacing/colors.

- `scripts/right-clicks.js` — optional context menu (Wiki link, skip toggle). Safe to remove if unwanted.

## How rendering works

- `scripts/render-items.js` fetches:
  - `data/generated/version.json` to decide whether to reuse a cached DOM snapshot from `localStorage`.
  - `data/generated/items.json` to get `imgUrl`/`wikiUrl` per item.
  - `data/sequence.json` to know which items to place and in what groups.
- Clicking an item toggles completion; state is saved in `localStorage`.

## Regenerating item metadata

Any time you change `data/sequence.json`, regenerate:

    python tools/build_items_json.py

This updates:

- `data/generated/items.json`
- `data/generated/version.json` (increments `cacheVersion` so clients drop stale cached HTML)

## Deploying to GitHub Pages

- You do not need a `CNAME` in this branch.
- Set Pages to serve from your repo (e.g., `main` / root). Commit the generated `data/generated/*` files.
- Your site will be at `https://<username>.github.io/<repo>/`.

## File structure (minimal)

    index.html
    data/
      sequence.json
      generated/
        items.json
        version.json
    scripts/
      render-items.js
      right-clicks.js
    styles/
      styles.css
      right-clicks.css
    tools/
      build_items_json.py
    .gitignore
    LICENSE
    README.md

## Notes and constraints

- Images are hotlinked from the OSRS Wiki via their public URLs in `items.json`.
- The script attempts to be respectful of the Wiki (uses a session + UA, retries with backoff).
- If an item can’t be resolved, it’s left out until it can be found.

## License and attribution

- Your code: license as you wish (this template keeps your existing license file).
- OSRS Wiki images and content: CC BY-NC-SA 3.0. Attribute the Wiki on your site (see footer in `index.html`).
