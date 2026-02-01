import pygame
from pygame.sprite import Sprite

def test_pygame_initialization() -> None:
    """Tests that pygame initializes successfully."""
    initialized,_ = pygame.init()
    assert initialized > 0
    pygame.quit()

def test_sprite_creation() -> None:
    """Tests the creation of a pygame sprite."""
    sprite = Sprite()
    assert isinstance(sprite, Sprite)
