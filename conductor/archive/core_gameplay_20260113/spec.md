# Specification: Core Gameplay Implementation

## 1. Overview

This track focuses on implementing the core gameplay mechanics as defined in "Phase 2: Core Gameplay (Muscles)" of the project's `README.md`. The goal is to build the foundational systems for combat, enemy behavior, and player interaction with the game world.

## 2. Key Features

### 2.1. Combat System
- **Player Attack:** Implement the player's primary melee attack, including animation, hitbox detection, and damage calculation.
- **Enemy Health & Damage:** Enemies must have a health component and be able to receive damage from the player's attacks.
- **Knockback Physics:** Both player and enemies should experience a slight knockback effect when hit to provide physical feedback.

### 2.2. Enemy AI
- **Basic Pathfinding:** Enemies will exhibit simple pathfinding behavior, moving towards the player when within a certain range.
- **Wandering Behavior:** When the player is not in range, enemies will wander around a defined area to make the world feel more alive.

### 2.3. Interaction System
- **NPC Dialogue:** Implement a system for displaying dialogue boxes with typing effects when the player interacts with NPCs.
- **Map Transitions:** Create the logic for moving the player between different maps (e.g., from the overworld into a dungeon or house).

### 2.4. Inventory Backend
- **Data Management:** Develop a simple data structure (e.g., a list or dictionary) to manage the player's inventory, such as collected items and currency (rupees). This is a non-visual, backend-only system for now.

## 3. Technical Requirements

- All code must adhere to the project's established coding standards and the `python.md` style guide.
- The implementation should be modular, with clear separation between combat, AI, and interaction logic to facilitate future expansion.
- The systems should be data-driven where possible (e.g., enemy stats defined in a configuration file or class) to allow for easy balancing and content creation.
