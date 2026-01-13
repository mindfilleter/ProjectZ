import pygame

from projectz.event_consumer import EventConsumer
from projectz.gamestates import GameStates


class ExploringEventConsumer(EventConsumer):
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.game.change_state(GameStates.Paused)
            elif event.key == pygame.K_e:
                self.game.change_state(GameStates.Inventory)
            elif event.key == pygame.K_RETURN:
                self.game.game_states[self.game.state].check_for_dialog()


class PausedEventConsumer(EventConsumer):
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.game.change_state(GameStates.Exploring)


class InventoryEventConsumer(EventConsumer):
    def __init__(self, game, inventory_state):
        self.game = game
        self.inventory_state = inventory_state

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.game.change_state(GameStates.Exploring)
            elif event.key == pygame.K_a:
                self.inventory_state.add_random_item()


class DialogEventConsumer(EventConsumer):
    def __init__(self, game, npc):
        self.game = game
        self.npc = npc

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.npc.cycle_dialogs()
                self.game.change_state(GameStates.Exploring)
