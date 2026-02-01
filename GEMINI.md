# Project MANDATORY Guidelines

## Build System
- **Build System**: Use Poetry for dependency management and Pytest for testing.

## Imports
- **Import Style**: NEVER use relative imports. Always use absolute imports from the `src` root.
- **Import Object Style**: Favor importing modules over objects.
  - **Correct**: `from projectz.engine import game` followed by `game.Game()`.
  - **Incorrect**: `from projectz.engine.game import Game`.

## Static Typing
- **Static Typing**: Strict typing is required. Mypy must pass with `strict = true` before any commit.

## AI Workflow
- **Architectural Changes**: Do NOT introduce architectural changes without user approval.

## Commit Policy
- **Commit Policy**: All changes must be small and atomic. Every change must be tested, confirmed to be working, and committed with a detailed message explaining the change.
