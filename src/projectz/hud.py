from pygame import sprite
from pygame import display
from pygame import draw
import pygame


class HealthBar(sprite.Sprite):
    X = 16
    Y = 16
    BAR_HEIGHT = 20
    BAR_WIDTH = 15
    BAR_SEPARATOR_WIDTH = 2
    COLOR = (255, 0, 0, 255)

    def __init__(self, player, *groups):
        super(HealthBar, self).__init__(*groups)
        self.player = player
        self.image = None
        self.rect = pygame.Rect(
            (HealthBar.X, HealthBar.Y), self._calculate_size()
        )
        self._previous_player_hp = 0

    def update(self):
        if self.image is None:
            self.image = pygame.Surface(
                self._calculate_size(), pygame.SRCALPHA
            )

        if self._previous_player_hp != self.player.hit_points:
            self._draw_health_bar()
            self._previous_player_hp = self.player.hit_points

    def _draw_health_bar(self):
        self.image.fill((0, 0, 0, 0))
        stencil = pygame.Rect(
            (0, 0), (HealthBar.BAR_WIDTH, HealthBar.BAR_HEIGHT)
        )

        for i in range(self.player.hit_points):
            draw.rect(self.image, "black", stencil)
            draw.rect(self.image, HealthBar.COLOR, stencil.inflate(-2, -2))
            stencil.move_ip(
                HealthBar.BAR_WIDTH + HealthBar.BAR_SEPARATOR_WIDTH, 0
            )

    def _calculate_size(self):
        separator_padding = (
            HealthBar.BAR_SEPARATOR_WIDTH
        ) * self.player.hit_point_max - 1

        health_bar_size = (
            (self.player.hit_point_max * HealthBar.BAR_WIDTH)
            + separator_padding,
            self.player.hit_point_max * HealthBar.BAR_HEIGHT,
        )

        return health_bar_size


class HUD(sprite.Group):
    def __init__(self, player, *sprites):
        super(HUD, self).__init__(*sprites)
        self.player = player
        self.add(HealthBar(player))
