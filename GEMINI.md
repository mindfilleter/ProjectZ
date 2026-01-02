# **Project Context & AI Instructions**

This document outlines the technical environment, constraints, and management tools for **Project Z**. All code generation and technical advice must adhere to these specifications.

## **1. Core Technology Stack**

*   **Language:** Python 3.13
*   **Game Library:** pygame
*   **Target Platforms:** Windows & Linux
    *   **Crucial Requirement:** All file path handling must be cross-platform. Use pathlib (preferred) or os.path.join. Avoid hardcoded backslashes (\) or forward slashes (/).

## **2. Environment Management**

This project uses **Poetry** for dependency management and packaging.

*   **Dependency Management:**  
    *   Do not use pip install directly.  
    *   Use poetry add <package_name> for runtime dependencies.  
    *   Use poetry add --group dev <package_name> for development dependencies.
*   **Running the Game:**  
    *   Execution command: poetry run python main.py (or specific entry point).

## **3. Version Control & Repository**

*   **System:** Git  
*   **Remote Repository:** [https://github.com/mindfilleter/ProjectZ](https://github.com/mindfilleter/ProjectZ)  
*   **Workflow:**  
    *   Ensure poetry.lock is committed to keep dependencies synchronized across Windows and Linux environments.  
    *   Use standard .gitignore practices for Python (exclude __pycache__, .venv, etc.).

## **4. Coding Standards**

*   **Style:** Strict adherence to **PEP-8** guidelines (naming conventions, indentation, whitespace).  
*   **Type Hinting:** **Do not use type hints.** Keep function signatures clean and simple to accommodate beginner skill levels.  
*   **Testing:** No automated unit testing/frameworks. Focus on manual playtesting.  
*   **Structure:** Code should be modular to support the "Phase 1: Engine" roadmap (separating Map, Player, and Logic).

## **5. Agent-Specific Instructions**

*   **Shell Command Safety:** When using `run_shell_command` with commands that take multi-line string arguments (e.g., `git commit -m`), do not pass a single string with newlines. Instead, use multiple flags for each line (e.g., `git commit -m 

## **6. Animation System**

The project uses a data-driven animation system that relies on JSON files to define animations for sprites. This approach allows for easy creation and modification of animations without altering Python code.

### **JSON File Structure**

For each spritesheet (e.g., `player.png`), there must be a corresponding JSON file named `player.png.spritesheet.json` in the same directory.

The structure of the JSON file is as follows:

```json
{
  "head": {
    "frame_width": 16,
    "frame_height": 16
  },
  "animations": {
    "idle_down": [
      [0, 100]
    ],
    "walk_down": [
      [0, 100],
      [1, 100],
      ["goto", 0]
    ]
  }
}
```

*   **`head`**: Contains metadata about the spritesheet.
    *   `frame_width`: The width of a single animation frame in pixels.
    *   `frame_height`: The height of a single animation frame in pixels.
*   **`animations`**: A dictionary where each key is an animation name (e.g., `"walk_down"`) and the value is an array of frame data.

### **Frame Data**

Each element in the animation array represents a step in the animation sequence. It can be one of two types:

1.  **Frame Display**: `[frame_index, duration]`
    *   `frame_index` (integer): The zero-based index of the frame to display from the spritesheet, calculated from left to right, top to bottom.
    *   `duration` (integer, optional): The number of milliseconds to display this frame. If omitted, a default of 100ms is used.
2.  **Special Command**: `["command", value]`
    *   `"goto"`: Jumps the animation to a specific frame index, allowing for loops. `["goto", 0]` will loop the animation back to the beginning.

### **Creating a New Animated Sprite**

To create a new animated entity:
1.  Inherit from the `AnimatedSprite` class located in `src/projectz/animated_sprite.py`.
2.  In your new class's `__init__`, call the parent constructor with the path to the spritesheet: `super().__init__("path/to/your/spritesheet.png")`.
3.  The `AnimatedSprite` class will automatically load the corresponding `.spritesheet.json` file.
4.  In your class's `update` method, set the `self.state` attribute to the desired animation name (e.g., `"walk_up"`) and call `self.update_animation(dt)`.