# Python Virtual Tabletop & Character Manager

This project is a comprehensive, expandable virtual tabletop (VTT) and character management suite for tabletop role-playing games, built with Python and PyQt6. It is designed from the ground up to be data-driven and highly extensible through a powerful plugin system, allowing users to easily add their own classes, races, items, and even complex game logic.

## Core Concepts: A Data-Driven Engine

The central philosophy of this project is that the application should be a "rules engine," not a hardcoded rulebook. The core application knows as little as possible about the specific rules of any game. Instead, it reads all game data—classes, spells, items, etc.—from simple data files at runtime.

### The Plugin System

All game content is loaded from the `plugins` directory. A plugin is simply a folder containing a `meta.json` manifest and subdirectories for its content. The "Core 5e Rules" are implemented as the default-enabled plugin.

- **`meta.json`:** Every plugin must have a `meta.json` file. This manifest tells the engine what the plugin is, who made it, what its version is, and, most importantly, how to load it. It defines dependencies and load order, ensuring that plugins which modify others are loaded correctly.

- **Data Files (`.json`):** The static properties of all game elements are defined in simple, human-readable JSON files. For example, the Fighter class, its proficiencies, and its level-up features are all defined in `fighter.json`. This allows users to create their own content (e.g., a homebrew class) simply by creating a new JSON file, with no programming required.

- **Scripting (`.lua` - Planned):** For complex game logic that cannot be described by data alone (e.g., the unique effects of a spell), the system is designed to eventually support lightweight, sandboxed Lua scripts. This provides maximum flexibility while maintaining application security and stability.

## Current Features

### Character Editor
A fully-featured character sheet editor with a multi-tab interface.
- **Dynamic Character Creation:** The "Class" dropdown is populated dynamically by reading all class `.json` files found in the plugin directories.
- **Live Calculations:** The sheet is fully reactive. Changing an ability score, level, or proficiency checkbox instantly recalculates and updates all derived stats, including:
  - Ability Modifiers
  - Proficiency Bonus
  - Skill Totals
  - Saving Throw Totals
- **Full Save/Load:** Characters can be saved to and loaded from a custom `.dndc` file format. This file includes all character data, proficiencies, and even the character's sprite.
- **Sprite Upload:** Click to upload a custom character image, which is saved as part of the character file.
- **Roleplay Tab:** A dedicated section for personality traits, ideals, bonds, flaws, and character backstory.
- **Integrated Dice Roller:** A powerful dice roller is accessible from the character sheet.

### uVTT Editor
A powerful editor for creating and preparing virtual tabletop maps.
- **Map & Image Loading:** Import any image to use as a map background.
- **Advanced Camera Controls:** Smooth panning with the middle mouse button and scroll wheel, and zooming with Ctrl+Scroll.
- **Dynamic Grid System:** Overlay a square or hexagonal grid on any map. The grid size is fully adjustable and scales with the map.
- **Contextual Toolbars:** A dynamic, two-tiered toolbar system. Selecting a main tool (e.g., "Drawing," "Fog of War") reveals a secondary toolbar with the specific tools for that context.

### Dice Roller Module
A robust dice string parser and roller.
- **Complex Syntax:** Supports standard rolls (`2d6`), advantage/disadvantage (`1d20A`, `1d20D`), keep highest/lowest (`4d6kh3`), flat modifiers, and complex combinations.
- **Clear Results:** Displays a clear, broken-down summary of each component of the roll and the grand total.

## Future Plans

- **Inventory System:** A drag-and-drop inventory and equipment management tab.
- **Spellbook:** A dedicated tab to manage known, prepared, and available spells based on the character's class and level.
- **DM Editor:** A tool for creating and managing custom items, NPCs, and encounters.
- **VTT Renderer:** A separate mode for "playing" on a map, with token movement, vision, and lighting.
- **Full Scripting Integration:** Implementing the Lua scripting engine to handle complex features and abilities.

## Technology Stack

- **Backend:** Python 3
- **UI Framework:** PyQt6
- **Data Format:** JSON
- **Scripting (Planned):** Lua
