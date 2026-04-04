# Ladlor's Interactive Gear Progression Chart & Chart builder

An interactive chart for Old School RuneScape Ironman progression, as well as web-UI based tooling for building charts.
Developed with the Ironscape Discord community to help players plan gear and skill unlocks in a clear, trackable order.

## Features

- **Interactive Tracking**: Click items or skills to mark them as acquired.
- **Progress Saved Locally**: Uses browser localStorage (no accounts, no servers).
- **Community Sequenced**: Based on collaborative theorycrafting and guides.
- **Building Charts**: Sequence almost anything exactly how you want.
- **Share your vision**: Share your custom charts with unique urls.

## Usage

- **Live site**: [ladlorchart.com](https://ladlorchart.com)
- Click any item/skill to toggle completion.
- Hover (or long-press on mobile) for item names and Wiki links.
- To reset your progress: clear this site’s local storage in your browser.

## For developers

If you want to fork or adapt this project:

- Start in `frontend/` for the React/Vite app.
- Start in `backend/` for the FastAPI API and backend-specific docs.
- Frontend Node version is pinned in `frontend/.nvmrc` (`nvm use` inside `frontend/`).
- Core chart sequencing lives in `data/logic/sequence.json`.
- Item metadata is generated into `data/generated/items.json` by `tools/build_items_json.py`.

For a **minimal, ready-to-fork template** (without site extras like changelog, FAQ, pagecount), see the [`minimal-template` branch](https://github.com/Madssb/InteractiveGearProg/tree/minimal-template).

## Repository structure

This section is intentionally high-level. It maps the main directories at the project root so it is easier to re-orient yourself quickly without trying to catalog every important file.

| **Path** | **Purpose** |
| --- | --- |
| `frontend/` | React/Vite frontend for the interactive chart UI and chart builder. |
| `backend/` | FastAPI backend, local development entrypoint, and backend tests. |
| `data/` | Chart sequencing data, generated metadata, and static content consumed by the app. |
| `tools/` | Utility scripts for generating or refreshing project data. |
| `osrswiki_images/` | Supporting package for resolving item image and wiki metadata. |
| `docs/` | Project documentation, deployment notes, and reference material. |
| `infra/` | Infrastructure-related files such as systemd units and cloudflared configs. |
| `discord_bot/` | Discord bot code related to the wider project ecosystem. |
| `.github/` | GitHub Actions workflows and repository automation. |

## Acknowledgments

Thanks to the **Ironscape Discord community** for sequencing and QA.  
Notable contributions:

- _So Iron Bruh_ — QA, co-author of **BRUHSailer**.
- _Parasailer_ — Author of **Parasailer’s Gear Progression Chart**, co-author of **BRUHSailer**.
- _Drøgøn_ — QA and theorycrafting for new metas.
- _Raze_ — QA and feedback.

## License

- **Code**: MIT (see `LICENSE`).
- **Images**: Not included in this repo. The chart hotlinks icons from the [Old School RuneScape Wiki](https://oldschool.runescape.wiki/), licensed under [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).

If you fork or host your own version, include attribution to the OSRS Wiki as shown in `frontend/index.html`.
