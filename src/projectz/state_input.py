from projectz.event_consumer import EventConsumer
from projectz.gamestates import GameStates
from projectz.input import input_manager
import pygame


class ExploringEventConsumer(EventConsumer):
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            action = input_manager.get_action(event, self.game.state)
            if action == "pause":
                self.game.change_state(GameStates.Paused)
            elif action == "action":
                self.game.game_states[self.game.state].check_for_dialog()


class PausedEventConsumer(EventConsumer):
    def __init__(self, game):
        self.game = game
        self.key_down_received = False

    def handle_event(self, event):
        action = input_manager.get_action(event, self.game.state)
        if action == "pause":
            if event.type == pygame.KEYDOWN:
                self.key_down_received = True
            elif event.type == pygame.KEYUP:
                if self.key_down_received:
                    self.game.change_state(GameStates.Exploring)
                    self.key_down_received = False



class InventoryEventConsumer(EventConsumer):
    def __init__(self, game, inventory_state):
        self.game = game
        self.inventory_state = inventory_state

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            action = input_manager.get_action(event, self.game.state)
            if action == "action":
                self.inventory_state.add_random_item()


class DialogEventConsumer(EventConsumer):
    def __init__(self, game, dialog_state):
        self.game = game
        self.dialog_state = dialog_state

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            action = input_manager.get_action(event, self.game.state)
            if action == "confirm":
                self.dialog_state.advance_dialog()
            elif action == "cancel":
                self.game.change_state(GameStates.Exploring)
