"""
This module handles the input management for the game.
"""
import pygame

from projectz.config import DEFAULT_CONTROLS
from projectz.gamestates import GameStates


class InputManager:
    """
    Manages the input for the game.
    """

    def __init__(self):
        """
        Initializes the input manager.
        """
        self.key_map = DEFAULT_CONTROLS
        self.exploring_action_map = self._get_action_map(
            ["up", "down", "left", "right", "action", "pause"]
        )
        self.paused_action_map = self._get_action_map(["pause"])
        self.inventory_action_map = self._get_action_map(["action"])
        self.dialog_action_map = self._get_action_map(["confirm", "cancel"])

        self.state_action_maps = {
            GameStates.Exploring: self.exploring_action_map,
            GameStates.Paused: self.paused_action_map,
            GameStates.Inventory: self.inventory_action_map,
            GameStates.Dialog: self.dialog_action_map,
        }

    def _get_action_map(self, actions):
        """
        Returns a map from key codes to actions for a given list of actions.
        """
        action_map = {}
        for action in actions:
            if action in self.key_map:
                key_code = self.key_map[action]
                action_map[key_code] = action
        return action_map

    def get_action(self, event, game_state):
        """
        Returns the action for a given event and game state.
        """
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            if game_state in self.state_action_maps:
                return self.state_action_maps[game_state].get(event.key)
        return None


# A global instance for easy access
input_manager = InputManager()
