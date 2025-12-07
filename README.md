# **Me and Papai’s Game Project**

*Inspired by The Legend of Zelda 1*

## **1\. Project Overview**

A top-down, real-time action-adventure game built in Python. The player explores a non-linear world, solves dungeon puzzles, and rescues a captive royal figure.

## **2\. Core Design Pillars**

### **A. Gameplay & Combat**

* **Real-time Combat:** Melee-focused fighting system.  
* **Boss Battles:** Multi-phase encounters requiring pattern recognition and specific strategies.  
* **Bestiary:** A wide variety of enemy types with unique behaviors.  
* **Secrets:** Hidden rooms ("Trickery") and walls to encourage discovery.

### **B. World & Exploration**

* **Non-Linearity:** The game world is open; dungeons and objectives can be tackled in various orders.  
* **Dungeon Design:** Complex interiors featuring:  
  * Puzzles and Traps  
  * Locked Doors & Keys mechanics  
  * **Lore:** Story context revealed upon completion.  
* **Exploration First:** The primary loop drives the player to uncover the map fog.

### **C. Progression Systems**

* **Constant Value Upgrades:**  
  * Heart Containers (Max HP)  
  * Magic/Stamina Meter extensions  
* **Item Gating:** Unique items found in dungeons unlock new areas or combat abilities.  
* **Guidance:** An in-game guide or NPC assistance system to help lost players.

## **3\. Tech Stack & Architecture**

* **Language:** Python  
* **Map Editor:** [Tiled](https://www.mapeditor.org/) (TMX/JSON format)  
* **Rendering Logic:**  
  * **Map Surface:** Static background layers.  
  * **Entity Surface:** Dynamic sprites (Player, Enemies).  
  * **Collision Surface:** Invisible layer for physics boundaries.

## **4\. Development Roadmap**

### **Phase 1: The Engine (Skeleton)**

*Focus on getting a character moving in a world.*

1. **Project Setup:** Directory structure for assets, code, and maps.  
2. **Map Loading:** Script to import "Tiled" maps and render them to the screen.  
3. **Player Controller:**  
   * Basic movement (Up, Down, Left, Right).  
   * State machine (Idle, Walking).  
4. **Collision System:** Implementing the "Collision Surface" logic to stop player movement against walls.  
5. **Camera/Scrolling:** Logic to keep the player centered or transition between map screens.

### **Phase 2: Core Gameplay (Muscles)**

*Focus on interaction and combat.*

1. **Combat System:**  
   * Attack animation and hitboxes.  
   * Enemy hurtboxes and health calculation.  
   * Knockback physics.  
2. **Enemy AI:** Basic pathfinding (moving toward player) and random wandering.  
3. **Interaction System:**  
   * **Dialogue:** Text box UI and typing effects for NPCs.  
   * **Map Transitions:** Teleportation logic between Overworld and Dungeons.  
4. **Inventory Data:** Backend list managing current items and rupees.

### **Phase 3: Content Expansion (Skin)**

*Focus on filling the world.*

1. **Dungeon Logic:** implementing locked doors, keys, and chest opening states.  
2. **Puzzle Elements:** Pushable blocks, floor switches, and pressure plates.  
3. **Asset Integration:**  
   * Importing final sprite work (Player, Enemies, Tilesets).  
   * Sound Effects (SFX) for hits, steps, and menu blips.  
4. **HUD/UI:** displaying Hearts, Magic Meter, and equipped item.

### **Phase 4: Polish & Audio (Soul)**

*Focus on game feel and atmosphere.*

1. **Music System:** Looping tracks for Overworld, Dungeon, and Boss themes.  
2. **Visual FX:** Particle effects for hits, dust when walking, death animations.  
3. **Game Guide:** Implementing the help system/menu.  
4. **Balancing:** Tweaking enemy health, damage values, and drop rates.