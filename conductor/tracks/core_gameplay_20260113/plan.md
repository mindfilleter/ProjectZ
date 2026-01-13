# Plan: Core Gameplay Implementation

This plan outlines the phases and tasks required to implement the core gameplay systems.

---

## Phase 1: Combat System Foundation

*Objective: Build the fundamental components of the combat system.*

- [x] **Task:** Create a `HealthComponent` class that can be attached to both the player and enemies to manage hit points. [e2d349c]
- [ ] **Task:** Implement the player's attack animation and create a corresponding hitbox that appears during the attack swing.
- [ ] **Task:** Add `HurtboxComponent` to enemies to detect collisions with the player's attack hitbox.
- [ ] **Task:** Implement a basic damage calculation system when a hitbox and hurtbox overlap.
- [ ] **Task:** Develop a knockback function that applies a brief, opposing force to an entity upon being hit.
- [ ] **Task:** Conductor - User Manual Verification 'Combat System Foundation' (Protocol in workflow.md)

## Phase 2: Enemy AI & Behavior

*Objective: Bring enemies to life with basic AI and movement.*

- [ ] **Task:** Implement a "wandering" state for enemies, causing them to move randomly within a defined radius.
- [ ] **Task:** Implement a "chase" state that uses simple pathfinding (e.g., A* or direct line-of-sight movement) to move towards the player.
- [ ] **Task:** Create the logic for enemies to transition between "wandering" and "chase" states based on player proximity.
- [ ] **Task:** Conductor - User Manual Verification 'Enemy AI & Behavior' (Protocol in workflow.md)

## Phase 3: World Interaction

*Objective: Enable player interaction with NPCs and the environment.*

- [ ] **Task:** Design and implement a UI element for displaying dialogue boxes.
- [ ] **Task:** Create a "typing effect" for text appearing in the dialogue box.
- [ ] **Task:** Develop an interaction system that triggers dialogue when the player is near an NPC and presses an action button.
- [ ] **Task:** Implement trigger zones or objects on the map that initiate a map transition when the player enters them.
- [ ] **Task:** Conductor - User Manual Verification 'World Interaction' (Protocol in workflow.md)

## Phase 4: Backend & Integration

*Objective: Set up the inventory data structure and integrate all new systems.*

- [ ] **Task:** Create a simple Python class or dictionary to manage player inventory data (e.g., `player.inventory['rupees']`).
- [ ] **Task:** Integrate the new combat, AI, and interaction systems into the main game loop.
- [ ] **Task:** Place a few test enemies and an NPC on a map to verify all systems work together correctly.
- [ ] **Task:** Conductor - User Manual Verification 'Backend & Integration' (Protocol in workflow.md)
