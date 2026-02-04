import enum
from typing import Optional

import pygame

from projectz.core import entity
from projectz.core import fsm
from projectz.ui import component

BUTTON_CLICKED = pygame.USEREVENT + 1


class ButtonState(enum.Enum):
    NORMAL = enum.auto()
    HOVER = enum.auto()
    CLICKED = enum.auto()


class ButtonComponent(entity.Component, fsm.FSMMixin):
    fsm_transitions = [
        (ButtonState.NORMAL, {ButtonState.HOVER}),
        (ButtonState.HOVER, {ButtonState.NORMAL, ButtonState.CLICKED}),
        (ButtonState.CLICKED, {ButtonState.HOVER}),
    ]
    fsm_initial_state = ButtonState.NORMAL

    def __init__(
        self,
        button_id: str,
        normal_color: pygame.Color,
        hover_color: pygame.Color,
        clicked_color: pygame.Color,
    ) -> None:
        entity.Component.__init__(self)
        fsm.FSMMixin.__init__(self)

        self.button_id = button_id
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.clicked_color = clicked_color
        self.original_pos: Optional[tuple[float, float]] = None

    @fsm.on_fsm_enter(ButtonState.NORMAL)
    def on_normal(self: "ButtonComponent") -> None:
        if (
            self.owner
            and hasattr(self.owner, "rect")
            and self.owner.rect
            and component.RenderComponent in self.owner
        ):
            render_comp = self.owner[component.RenderComponent]
            render_comp.color = self.normal_color
            render_comp.redraw()
            if self.original_pos is not None:
                self.owner.rect.topleft = self.original_pos

    @fsm.on_fsm_enter(ButtonState.HOVER)
    def on_hover(self: "ButtonComponent") -> None:
        if (
            self.owner
            and hasattr(self.owner, "rect")
            and self.owner.rect
            and component.RenderComponent in self.owner
        ):
            render_comp = self.owner[component.RenderComponent]
            render_comp.color = self.hover_color
            render_comp.redraw()
            if self.original_pos is not None:
                self.owner.rect.topleft = self.original_pos

    @fsm.on_fsm_enter(ButtonState.CLICKED)
    def on_clicked(self: "ButtonComponent") -> None:
        if (
            self.owner
            and hasattr(self.owner, "rect")
            and self.owner.rect
            and component.RenderComponent in self.owner
        ):
            render_comp = self.owner[component.RenderComponent]
            if self.original_pos is None:
                self.original_pos = self.owner.rect.topleft

            render_comp.color = self.clicked_color
            render_comp.redraw()

            if self.original_pos is not None:
                pressed_pos = (
                    self.original_pos[0] + render_comp.shadow_offset,
                    self.original_pos[1] + render_comp.shadow_offset,
                )
                self.owner.rect.topleft = pressed_pos

    def handle_event(self, pygame_event: pygame.event.Event) -> bool:
        if not self.owner or not hasattr(self.owner, "rect") or not self.owner.rect:
            return False

        consumed = False
        if pygame_event.type == pygame.MOUSEMOTION:
            if self.owner.rect.collidepoint(pygame_event.pos):
                if self.current_state == ButtonState.NORMAL:
                    self.change_state(ButtonState.HOVER)
                    consumed = True
            elif self.current_state == ButtonState.HOVER:
                self.change_state(ButtonState.NORMAL)
                consumed = True
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            if self.owner.rect.collidepoint(pygame_event.pos):
                self.change_state(ButtonState.CLICKED)
                consumed = True
        elif pygame_event.type == pygame.MOUSEBUTTONUP:
            if self.current_state == ButtonState.CLICKED:
                self.change_state(ButtonState.HOVER)
                if self.owner.rect.collidepoint(pygame_event.pos):
                    pygame.event.post(
                        pygame.event.Event(BUTTON_CLICKED, {"button_id": self.button_id})
                    )
                consumed = True
        return consumed

    def update(self, dt: int) -> None:
        self.update_fsm(dt)


def create_button(
    size: tuple[int, int],
    text: str,
    button_id: str,
    normal_color: pygame.Color,
    hover_color: pygame.Color,
    clicked_color: pygame.Color,
    *groups: pygame.sprite.AbstractGroup[entity.Entity],
    border_radius: int = 8,
) -> entity.Entity:
    button_entity = entity.Entity(*groups)

    render_comp = component.RenderComponent(
        size=size,
        text=text,
        color=normal_color,
        border_radius=border_radius,
    )
    button_entity.add_components(render_comp)

    button_comp = ButtonComponent(
        button_id=button_id,
        normal_color=normal_color,
        hover_color=hover_color,
        clicked_color=clicked_color,
    )
    button_entity.add_components(button_comp)

    button_entity.image = render_comp.image
    button_entity.rect = render_comp.rect

    return button_entity
