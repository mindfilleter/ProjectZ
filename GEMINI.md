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