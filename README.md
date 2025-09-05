# Ladlor's Interactive Gear Progression Chart

Welcome to Ladlor's Interactive Gear Progression Chart! This tool provides a suggested sequence of unlocks for players of Old School RuneScape, specifically tailored for Ironman mode. Developed collaboratively by Ladlor and contributors from the Ironscape Discord community, this chart aims to help Ironman players optimize their gear progression efficiently.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Usage](#usage)
- [Local Development](#Local-development)
- [Contributing](#contributing)
- [For Developers](#for-developers)
- [File Structure](#file-structure)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Introduction

Ironman mode in Old School RuneScape (OSRS) offers a challenging experience where players are entirely self-sufficient, unable to trade with others. This gear progression chart is designed to guide Ironman players through an optimal path of gear and skill upgrades, enhancing their gameplay and progression.

The chart is interactive, allowing players to track their progress by marking items and skills they've acquired. It provides a visual representation of the recommended order in which to obtain gear and unlocks, helping players plan their journey effectively.

## Features

- **Interactive Tracking**: Click on items and skills to mark them as acquired, which will be saved locally on your browser.
- **Visual Progression Path**: A clear, visual representation of the suggested gear and skill acquisition sequence.
- **Easy to Use**: Simply open the HTML file in your browser to start using the chart.
- **Persistent State**: Your progress is saved locally, so you can return to the chart without losing your tracked items.
- **Tailored for Ironman**: Specifically designed with the Ironman gameplay style in mind.

## Usage

1. **Access the Chart**: Visit [https://madssb.github.io/InteractiveGearProg/index.html](https://madssb.github.io/interactiveGearProg) to use the chart directly in your browser.
2. **Track Progress**: Click on any gear item or skill icon to mark it as acquired. Progress is saved locally in your browser and will persist between visits.
3. **Resetting Progress**: To reset your progress, clear your browser's local storage for this site.

## Local Development

Running the chart locally is useful for offline access or for contributors who want to customize the progression sequence for their own needs. This flexibility allows for tailoring the tool to different game modes or personal preferences.

If you want to modify or host the chart locally, follow these steps:

1. **Clone or Download** this repository.
2. Ensure the following files are in the same directory:
   - `index.html`
   - `styles/` (containing `styles.css` and `right-clicks.css`)
   - `scripts/` (containing `render-items.js` and `right-clicks.js`)
   - `images/` folder with all required icons.
3. **Open** `index.html` in your browser.
4. **Make Changes**: Modify the JSON or JavaScript files to customize the chart.

## Contributing

We welcome contributions from the community to improve this gear progression chart. If you have suggestions, bug reports, or wish to add features, please follow these steps:

1. **Fork the Repository**: Create a fork of this project to your own GitHub account.
2. **Make Changes**: Modify the codebase as you see fit. Ensure compatibility with the existing structure.
3. **Submit a Pull Request**: Once your changes are ready, submit a pull request for review.
4. **Review Process**: Contributors will review your pull request and provide feedback or merge it into the main project.

## For Developers

This project is built with plain HTML, CSS, and JavaScript, with no external dependencies. The chart’s interactivity relies on browser localStorage for tracking user progress. Key scripts include:

- `render-items.js`: Fetches JSON data and renders the chart dynamically.
- `right-clicks.js`: Adds a custom context menu for enhanced interactivity.

### Development Workflow

- Edit the JSON files in `data/` to update the chart’s sequence or items.
- Modify the JavaScript in `scripts/` for new features or bug fixes.

## File Structure

| **Directory/File**    | **Description**                                               |
| --------------------- | ------------------------------------------------------------- |
| `index.html`          | Main entry point for the interactive chart.                   |
| `data/`               | Contains JSON files for defining item and skill sequences.    |
| └─ `items.json`       | Metadata for each item, including image source and wiki link. |
| └─ `sequence.json`    | Defines the order of items and skills in the chart.           |
| `scripts/`            | JavaScript files for rendering and interactive behavior.      |
| └─ `render-items.js`  | Handles chart rendering and interactive features.             |
| └─ `right-clicks.js`  | Implements the custom right-click menu.                       |
| `styles/`             | CSS files for styling the chart and context menu.             |
| └─ `styles.css`       | Main stylesheet for the chart.                                |
| └─ `right-clicks.css` | Styles for the right-click context menu.                      |

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)](https://creativecommons.org/licenses/by-nc-sa/3.0/) license.

All images are sourced from the OSRS Wiki, which also follows the same license.
